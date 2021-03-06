# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-10 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0013_auto_20180627_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='educationdegree',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='education_degrees', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='branch_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.Branch'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='contract_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.Contract'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='degree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.Degree'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.Department'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='education_degree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.EducationDegree'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.Gender'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='id_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.IdDocument'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='military_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.MilitaryStatus'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='citizen_employees', to='countries.Nationality'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='place_of_birth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='born_in_employees', to='countries.City'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='religion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.Religion'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.Section'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='social_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='employees.SocialStatus'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='sub_section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='companies.SubSection'),
        ),
        migrations.AlterField(
            model_name='gender',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='genders', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='iddocument',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='id_documents', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='militarystatus',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='military_status', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='religion',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='religions', to='companies.Company'),
        ),
        migrations.AlterField(
            model_name='socialstatus',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='social_status', to='companies.Company'),
        ),
    ]
