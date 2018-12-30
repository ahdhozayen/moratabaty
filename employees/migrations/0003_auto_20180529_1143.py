# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 09:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_auto_20180522_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='branch_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.Branch'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='contract_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.Contract'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='degree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.Degree'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.Department'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='education_degree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.EducationDegree'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='field_of_study',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.Gender'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='id_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='id_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.IdDocument'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='military_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.MilitaryStatus'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='citizen_employees', to='countries.Nationality'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='place_of_birth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='born_in_employees', to='countries.City'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='religion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.Religion'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.Section'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='social_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.SocialStatus'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='sub_section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.SubSection'),
        ),
    ]
