# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-22 15:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_delete_emailtemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requester',
            name='email',
            field=models.EmailField(error_messages={'unique': 'هذا البريد الالكترونى مسجل لدينا من قبل !'}, max_length=254, unique=True),
        ),
    ]
