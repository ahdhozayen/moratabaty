# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-25 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_remove_attendance_is_final'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_final',
            field=models.BooleanField(default=False),
        ),
    ]