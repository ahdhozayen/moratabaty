# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-10 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='country_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='countries.Country'),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='country_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='countries.Country'),
        ),
    ]