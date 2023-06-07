from datetime import datetime
from uuid import uuid4

import phonenumbers
from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumbers import NumberParseException

from . import config


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(
        _('created'), default=datetime.now, blank=True, null=False)

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(
        _('modified'), default=datetime.now, blank=True, null=False)

    class Meta:
        abstract = True


def check_phone(phone: str):
    try:
        ph_num = phonenumbers.parse(phone)
        return phonenumbers.is_valid_number(ph_num)
    except NumberParseException:
        raise ValidationError(
            f'Your phone {phone} is not a real phone number.',
            params={'value': phone}
        )


class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    unknown = '-'
    woman = 'W'
    man = 'M'
    client_name = models.CharField(
        _('client name'), max_length=config.CF_DEFAULT)
    client_surname = models.CharField(
        _('client surname'), max_length=config.CF_DEFAULT)
    CHOICES = (
              (woman, 'женский'),
              (man, 'мужской'),
              (unknown, '-'),
    )
    sex = models.CharField(_('sex'), max_length=1,
                           choices=CHOICES, default=unknown)
    date_of_birth = models.DateField(_('date of birth'))
    email = models.EmailField(_('email'), blank=True, null=True)
    phone = models.CharField(
        _('phone'), max_length=config.CF_DEFAULT, validators=[check_phone])
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.DecimalField(
        max_digits=config.DECIMAL_MAX_DIGITS,
        decimal_places=config.DECIMAL_PLACES,
        default=0,
    )

    def __str__(self):
        return f"{self.client_surname} {self.client_name}"

    class Meta:
        db_table = 'client'
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class PersonalData(UUIDMixin, CreatedMixin, ModifiedMixin):
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    allergies = models.TextField(_('allergies'), blank=True, null=True)
    medications_taken = models.TextField(
        _('medications taken'), blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

    def __str__(self):
        return f"{self.client_id}"

    class Meta:
        db_table = 'personal_data'
        verbose_name_plural = _('personal data')


class Doctor(UUIDMixin, CreatedMixin, ModifiedMixin):
    name = models.CharField(_('name'), max_length=config.CF_DEFAULT)
    surname = models.CharField(_('surname'), max_length=config.CF_DEFAULT)
    speciality = models.CharField(
        _('speciality'), max_length=config.CF_DEFAULT)
    description = models.CharField(
        _('description'), max_length=config.CF_DEFAULT)
    sex = models.CharField(_('sex'), max_length=config.CF_DEFAULT)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    email = models.CharField(
        _('email'), max_length=config.CF_DEFAULT, blank=True, null=True)
    phone = models.CharField(
        _('phone'), max_length=config.CF_DEFAULT, validators=[check_phone])
    office = models.CharField(_('office'), max_length=config.CF_DEFAULT)
    services = models.ManyToManyField(
        'Service', verbose_name=_('services'), through='DoctorToService')
    photo = models.TextField(_('photo'), blank=True, null=True)

    def __str__(self):
        return f"{self.surname} {self.name}"

    class Meta:
        db_table = 'doctor'
        verbose_name = _('doctor')
        verbose_name_plural = _('doctors')


def positive_int(num: int):
    if num <= 0:
        raise ValidationError(
            f'Value {num} is less or equal zero',
            params={'value': num}
        )


class Service(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.CharField(_('title'), max_length=config.CF_DEFAULT)
    description = models.TextField(_('description'), blank=True, null=True)
    duration = models.IntegerField(_('duration'))
    price = models.DecimalField(_('price'), max_digits=config.DECIMAL_MAX_DIGITS,
                                decimal_places=config.DECIMAL_PLACES, validators=[positive_int])
    appointments = models.ManyToManyField(
        'Appointment', through='ServiceToAppointment')
    doctors = models.ManyToManyField(Doctor, through='DoctorToService')
    photo = models.TextField(_('photo'), blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'service'
        verbose_name = _('service')
        verbose_name_plural = _('services')


class Appointment(UUIDMixin, CreatedMixin, ModifiedMixin):
    not_paid = 'NP'
    paid = 'P'
    CHOICES = (
              (not_paid, 'Не оплачено'),
              (paid, 'Оплачено'),
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    time_of_beginning = models.DateTimeField(
        _('time of beginning'), blank=False, null=False)
    time_of_ending = models.DateTimeField(
        _('time of ending'), blank=False, null=False)
    status_payment = models.CharField(
        _('status payment'), max_length=20, choices=CHOICES, default=not_paid)
    date_of_payment = models.DateTimeField(
        _('date of payment'), auto_now_add=True)
    services = models.ManyToManyField(Service, through='ServiceToAppointment')

    def __str__(self):
        return f'{self.time_of_beginning}, {self.client}, {self.status_payment}'

    class Meta:
        db_table = 'appointment'

    def validate_appointment(self) -> bool:
        try:
            doctors_app = Appointment.objects.all().filter(doctor__id=self.doctor.id)
        except ObjectDoesNotExist:
            return False
        for appointment in doctors_app:
            if appointment.time_of_beginning < self.time_of_beginning < appointment.time_of_ending:
                return False
            if appointment.time_of_beginning < self.time_of_ending < appointment.time_of_ending:
                return False
        return True

    def clean(self):
        super().clean()
        if self.time_of_beginning < timezone.now() or self.time_of_ending < timezone.now():
            raise ValidationError(
                'Time of beginning must be in future, not in the past.',
                params={'time_of_beginning': self.time_of_beginning,
                        'time_of_ending': self.time_of_ending},
            )
        if not self.time_of_ending:
            raise ValidationError(
                {'time_of_ending': 'time'},
                params={'time_of_ending': 'time'},
            )

        if not self.time_of_beginning:
            raise ValidationError(
                {'time_of_beginning': 'time'},
                params={'time_of_beginning': 'time'},
            )
        if self.time_of_ending <= self.time_of_beginning:
            raise ValidationError(
                {'time_of_beginning': _(
                    'Time of beginning must be less than time of ending.')},
                params={'time_of_beginning': self.time_of_beginning,
                        'time_of_ending': self.time_of_ending},
            )
        if not self.validate_appointment():
            raise ValidationError(
                'The doctor is busy at this time.',
                params={'time_of_beginning': self.time_of_beginning,
                        'time_of_ending': self.time_of_ending},
            )


class ServiceToAppointment(UUIDMixin, CreatedMixin, ModifiedMixin):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)

    class Meta:
        db_table = 'service_to_appointment'
        unique_together = (('service', 'appointment'),)


class DoctorToService(UUIDMixin, CreatedMixin):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        db_table = 'doctor_to_service'
        unique_together = (('doctor', 'service'),)
