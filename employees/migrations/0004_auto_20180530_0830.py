# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-30 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_auto_20180529_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='id_number',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
