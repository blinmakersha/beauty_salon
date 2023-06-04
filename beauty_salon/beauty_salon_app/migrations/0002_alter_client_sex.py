# Generated by Django 4.1.7 on 2023-05-04 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beauty_salon_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='sex',
            field=models.CharField(choices=[('W', 'женский'), ('M', 'мужской')], default='-', max_length=1, verbose_name='sex'),
        ),
    ]