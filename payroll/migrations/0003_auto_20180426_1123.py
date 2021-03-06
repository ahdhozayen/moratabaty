# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-26 09:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0002_auto_20180426_1012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salary',
            old_name='total_taxable_deducted_salary_element',
            new_name='total_taxable_deducted_salary_elements',
        ),
        migrations.AddField(
            model_name='salary',
            name='total_taxable_added_salary_elements',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salary',
            name='total_untaxable_added_salary_elements',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
