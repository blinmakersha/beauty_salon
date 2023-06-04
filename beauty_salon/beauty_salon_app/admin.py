from django.contrib import admin
from .models import Client, PersonalData, Doctor, Service, Appointment, ServiceToAppointment, DoctorToService
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

# class FormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         print(self.cleaned_data)
#         doctor = self.cleaned_data['doctor']
#         services = self.cleaned_data['service']
#         if all([service in doctor.services.all() for service in services.all()]):
#             # print([service.title for service in services])
#             # print([service.title for service in doctor.services])
#             raise ValidationError(
#                 'The doctor does not do such service.',
#                 params={'doctor': 'doctor does not do such services.'},
#             )

# class ServiceToAppointment_inline(admin.TabularInline):
#     model = ServiceToAppointment
#     formset = FormSet
#     extra = 1


class DoctorToService_inline(admin.TabularInline):
    model = DoctorToService
    extra = 1


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    model = Appointment
    # inlines = (ServiceToAppointment_inline,)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    model = Service
    inlines = (DoctorToService_inline,)
    # inlines = (ServiceToAppointment_inline, DoctorToService_inline,)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    model = Doctor
    inlines = (DoctorToService_inline,)


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    model = PersonalData


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
