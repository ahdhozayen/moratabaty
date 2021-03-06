# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-25 09:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=255)),
                ('section', models.CharField(max_length=255)),
                ('sub_section', models.CharField(max_length=255)),
                ('degree', models.CharField(max_length=255)),
                ('year', models.IntegerField(choices=[(2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (2030, 2030), (2031, 2031), (2032, 2032), (2033, 2033), (2034, 2034), (2035, 2035), (2036, 2036), (2037, 2037), (2038, 2038), (2039, 2039), (2040, 2040), (2041, 2041), (2042, 2042), (2043, 2043), (2044, 2044), (2045, 2045), (2046, 2046), (2047, 2047), (2048, 2048), (2049, 2049)], default=2018)),
                ('month', models.CharField(choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=10)),
                ('overtime_hours', models.FloatField()),
                ('total_working_days_in_month', models.IntegerField()),
                ('total_attended_days', models.FloatField()),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='DayOff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_days', models.FloatField()),
                ('attendance_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_offs', to='attendance.Attendance')),
            ],
        ),
        migrations.CreateModel(
            name='DayOffRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('salary_deduction_factor', models.FloatField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_off_rules', to='companies.Company')),
            ],
        ),
        migrations.AddField(
            model_name='dayoff',
            name='rule_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_offs', to='attendance.DayOffRule'),
        ),
        migrations.AlterUniqueTogether(
            name='dayoffrule',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('employee_id', 'year', 'month')]),
        ),
    ]
