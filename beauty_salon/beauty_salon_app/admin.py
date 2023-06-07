from django.contrib import admin

from .models import (Appointment, Client, Doctor, DoctorToService,
                     PersonalData, Service)


class DoctorToService_inline(admin.TabularInline):
    model = DoctorToService
    extra = 1


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    model = Appointment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    model = Service
    inlines = (DoctorToService_inline,)


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
