# Generated by Django 4.1.7 on 2023-05-04 15:54

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('time_of_beginning', models.DateTimeField(verbose_name='time of beginning')),
                ('time_of_ending', models.DateTimeField(verbose_name='time of ending')),
                ('status_payment', models.CharField(choices=[('NP', 'Не оплачено'), ('P', 'Оплачено')], default='NP', max_length=2, verbose_name='status payment')),
                ('date_of_payment', models.DateTimeField(auto_now_add=True, verbose_name='date of payment')),
            ],
            options={
                'db_table': 'appointment',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('client_name', models.CharField(max_length=40, verbose_name='client name')),
                ('client_surname', models.CharField(max_length=40, verbose_name='client surname')),
                ('sex', models.CharField(max_length=40, verbose_name='sex')),
                ('date_of_birth', models.DateField(verbose_name='date of birth')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email')),
                ('phone', models.CharField(max_length=40, verbose_name='phone')),
                ('money', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'db_table': 'client',
            },
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('name', models.CharField(max_length=40, verbose_name='name')),
                ('surname', models.CharField(max_length=40, verbose_name='surname')),
                ('speciality', models.CharField(max_length=40, verbose_name='speciality')),
                ('description', models.CharField(max_length=40, verbose_name='description')),
                ('sex', models.CharField(max_length=40, verbose_name='sex')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='date of birth')),
                ('email', models.CharField(blank=True, max_length=40, null=True, verbose_name='email')),
                ('phone', models.CharField(max_length=40, verbose_name='phone')),
                ('office', models.CharField(max_length=40, verbose_name='office')),
            ],
            options={
                'verbose_name': 'doctor',
                'verbose_name_plural': 'doctors',
                'db_table': 'doctor',
            },
        ),
        migrations.CreateModel(
            name='DoctorToService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.doctor')),
            ],
            options={
                'db_table': 'doctor_to_service',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('title', models.CharField(max_length=40, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
            ],
            options={
                'verbose_name': 'service',
                'verbose_name_plural': 'services',
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='ServiceToAppointment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.appointment')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.service')),
            ],
            options={
                'db_table': 'service_to_appointment',
                'unique_together': {('service', 'appointment')},
            },
        ),
        migrations.AddField(
            model_name='service',
            name='appointments',
            field=models.ManyToManyField(through='beauty_salon_app.ServiceToAppointment', to='beauty_salon_app.appointment'),
        ),
        migrations.AddField(
            model_name='service',
            name='doctors',
            field=models.ManyToManyField(through='beauty_salon_app.DoctorToService', to='beauty_salon_app.doctor'),
        ),
        migrations.CreateModel(
            name='PersonalData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('allergies', models.TextField(blank=True, null=True, verbose_name='allergies')),
                ('medications_taken', models.TextField(blank=True, null=True, verbose_name='medications taken')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.client')),
            ],
            options={
                'verbose_name_plural': 'personal data',
                'db_table': 'personal_data',
            },
        ),
        migrations.AddField(
            model_name='doctortoservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.service'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='services',
            field=models.ManyToManyField(through='beauty_salon_app.DoctorToService', to='beauty_salon_app.service', verbose_name='services'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.client'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beauty_salon_app.doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='services',
            field=models.ManyToManyField(through='beauty_salon_app.ServiceToAppointment', to='beauty_salon_app.service'),
        ),
        migrations.AlterUniqueTogether(
            name='doctortoservice',
            unique_together={('doctor', 'service')},
        ),
    ]
