from datetime import datetime, timedelta, timezone

import pytz
from django import forms
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models
from django.forms import (CharField, DateInput, DecimalField, EmailField,
                          EmailInput, Form, TextInput)
from django.forms.widgets import SelectDateWidget

from .config import (CF_DEFAULT, DECIMAL_MAX_DIGITS, DECIMAL_PLACES,
                     EMAIL_DEFAULT_LEN)
from .models import Appointment, Client, Doctor, DoctorToService, Service


class AddFundsForm(Form):
    money = DecimalField(label='Amount',
                         max_digits=DECIMAL_MAX_DIGITS,
                         decimal_places=DECIMAL_PLACES
                         )


class RegistrationForm(auth_forms.UserCreationForm):
    first_name = CharField(max_length=CF_DEFAULT, required=True)
    last_name = CharField(max_length=CF_DEFAULT, required=True)
    email = EmailField(max_length=EMAIL_DEFAULT_LEN, required=True)
    date_of_birth = forms.DateField(required=True)
    phone = CharField(max_length=CF_DEFAULT, required=True)

    class Meta:
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name',
                  'date_of_birth', 'email', 'phone', 'password1', 'password2']


class AppointmentForm(forms.Form):   # book an appointment
    # doctor is chosen from existing doctors in db
    doctor = forms.TypedChoiceField(label='')
    doctor.widget.attrs.update({'class': 'app-form-control'})
    # service is chosen from existing services in db
    service = forms.TypedChoiceField(label='')
    service.widget.attrs.update({'class': 'app-form-control'})
    app_date = forms.DateField(label='', widget=SelectDateWidget(
        years=range(2023, 2024)))  # appointment date
    app_date.widget.attrs.update({'class': 'app-form-control-date'})
    app_time = forms.TypedChoiceField(label='')  # time of appointment
    app_time.widget.attrs.update({'class': 'app-form-control'})
    status_payment = forms.TypedChoiceField(label='')
    status_payment.widget.attrs.update({'class': 'app-form-control'})

    def __init__(self, client, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.client = client
        self.fields['doctor'].choices = [(c.id, c.name + " " + c.surname + " (" + c.speciality + ")")
                                         for c in Doctor.objects.filter().all()]
        self.fields['service'].choices = [(c.id, c.title + " (" + str(c.duration) + "мин." + ", " + str(c.price) + "$" + ")")
                                          for c in Service.objects.filter().all()]
        self.fields['app_time'].choices = [('9:00 AM', '9:00 AM'), ('10:00 AM', '10:00 AM'), ('11:00 AM', '11:00 AM'),
                                           ('13:00 PM', '13:00 PM'), ('14:00 PM',
                                                                      '14:00 PM'), ('15:00 PM', '15:00 PM'),
                                           ('16:00 PM', '16:00 PM'), ('17:00 PM', '17:00 PM')]
        self.fields['status_payment'].choices = [
            ('NP', 'Оплатить Позже'), ('P', 'Оплатить Онлайн')]

    def get_beginning(self, data: dict):
        keys = 'app_date', 'app_time'
        if all([key in data.keys() for key in keys]):
            year, month, day = data['app_date'].year, data['app_date'].month, data['app_date'].day
            hour, minutes = [int(value)
                             for value in data['app_time'][:-3].split(':')]
            return datetime(year, month, day, hour, minutes)
        raise Exception('bad POST with form of appointment')

    def check_doc_to_service(self, doc_id, serv_id):
        has_service = False
        for service in DoctorToService.objects.filter(doctor__id=doc_id):
            if str(service.service_id) == str(serv_id):
                has_service = True
        if not has_service:
            self.add_error(
                'doctor', 'Выбранный вами доктор, не выполняет эту услугу. Попробуйте еще раз.')
        else:
            return True

    def check_balance(self, serv, st_payment):
        default = True
        if st_payment == "P":
            if self.client.money < serv.price:
                default = False
        if not default:
            self.add_error(
                'service', 'Недостаточное количество средств. Пополните баланс.')
        else:
            return True

    def validate_appointment(self, doc_id, beginning, time_of_ending) -> bool:
        doctors_app = Appointment.objects.all().filter(doctor__id=doc_id)
        for appointment in doctors_app:
            print(f'appointment.time_of_beginning: {appointment.time_of_beginning.replace(tzinfo=pytz.utc)},   \
                    appointment.time_of_ending: {appointment.time_of_ending}   \
                    beginning: {beginning.replace(tzinfo=pytz.utc)} time_of_ending: {time_of_ending}')
            if appointment.time_of_beginning < beginning.replace(tzinfo=pytz.utc) < appointment.time_of_ending:
                self.add_error(
                    'appointment', 'Текущее время уже занято, выберите другое.')
                return False
            if appointment.time_of_beginning < time_of_ending.replace(tzinfo=pytz.utc) < appointment.time_of_ending:
                self.add_error(
                    'appointment', 'Текущее время уже занято, выберите другое.')
                return False
            if beginning < datetime.now() or time_of_ending < datetime.now():
                self.add_error(
                    'app_date', 'Нельзя выбрать время в прошлом. Попробуйте еще раз.')
                return False
        return True

    def save(self):
        if self.is_valid():
            data = self.cleaned_data
            serv = Service.objects.get(id=data['service'])
            beginning = self.get_beginning(data)
            time_of_ending = beginning + timedelta(minutes=serv.duration)
            doc_id = data['doctor']
            serv_id = data['service']
            st_payment = data['status_payment']
            if st_payment == 'P':
                date_of_payment = datetime.now()
            else:
                date_of_payment = None
            # check if doctor is related to the service
            if self.check_doc_to_service(doc_id, serv_id):
                if self.check_balance(serv, st_payment):
                    if self.validate_appointment(doc_id, beginning, time_of_ending):
                        app = Appointment.objects.create(client=self.client, doctor_id=data['doctor'], time_of_beginning=beginning,
                                                         time_of_ending=time_of_ending, status_payment=st_payment,
                                                         date_of_payment=date_of_payment,)
                        app.services.set((serv_id,))
                        app.save()
                        return app
