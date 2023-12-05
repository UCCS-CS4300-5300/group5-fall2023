# Generated by Django 3.2.13 on 2023-11-21 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherApp', '0003_location_weather'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='address',
        ),
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='state',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]