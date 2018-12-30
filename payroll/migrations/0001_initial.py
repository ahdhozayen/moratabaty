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
            name='CustomPythonRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('help_text', models.TextField(default='\n    You can define a custom deduction/addition rule here using python code.\n    You have the following variables available to use:\n    * basic: this is the basic salary of the employee.\n    * variable: this is the variable salary of the employee.\n    * d_days: these are the number of days the employee should be deducted this month\n    because of his/her absence or any other Attendance rules that implies deduction days.\n    * grs:(without `o`) gross salary equals to basic salary + variable salary + any other added allowances/bonus/incentive etc..\n    After calculating your equation, you have to store the required amount to be added/deducted in a variable named amount.\n    If the value of the amount variable is positive, the amount will be added to the net salary of the employee.\n    And if it is negative, it will be deducted.\n    Example:\n    if basic <= 5000:\n    ____extra_deduction = -250\n    else:\n    ____extra_deduction = -500\n    amount = extra_deduction\n    Make Sure that your code is properly indented using 4 spaces\n    ')),
                ('rule_definition', models.TextField()),
                ('taxable', models.BooleanField(default=False)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_rules', to='companies.Company')),
            ],
        ),
        migrations.CreateModel(
            name='InsuranceRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('basic_deduction_percentage', models.FloatField()),
                ('variable_deduction_percentage', models.FloatField()),
                ('maximum_insurable_basic_salary', models.FloatField()),
                ('maximum_insurable_variable_salary', models.FloatField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurance_rules', to='companies.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=255)),
                ('section', models.CharField(max_length=255)),
                ('sub_section', models.CharField(max_length=255)),
                ('degree', models.CharField(max_length=255)),
                ('deducted_days', models.FloatField()),
                ('year', models.IntegerField(choices=[(2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (2030, 2030), (2031, 2031), (2032, 2032), (2033, 2033), (2034, 2034), (2035, 2035), (2036, 2036), (2037, 2037), (2038, 2038), (2039, 2039), (2040, 2040), (2041, 2041), (2042, 2042), (2043, 2043), (2044, 2044), (2045, 2045), (2046, 2046), (2047, 2047), (2048, 2048), (2049, 2049)], default=2018)),
                ('month', models.CharField(choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=10)),
                ('basic_salary', models.FloatField()),
                ('variable_salary', models.FloatField()),
                ('gross_salary', models.FloatField()),
                ('net_salary', models.FloatField()),
                ('custom_rule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='payroll.CustomPythonRule')),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='employees.Employee')),
                ('insurance_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='payroll.InsuranceRule')),
            ],
            options={
                'verbose_name_plural': 'Salaries',
            },
        ),
        migrations.CreateModel(
            name='SalaryElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('salary_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_elements', to='payroll.Salary')),
            ],
        ),
        migrations.CreateModel(
            name='SalaryElementType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('element_type', models.CharField(choices=[('addition', 'Addition'), ('deduction', 'Deduction')], max_length=255)),
                ('taxable', models.BooleanField(default=False)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_element_types', to='companies.Company')),
            ],
        ),
        migrations.CreateModel(
            name='TaxRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('personal_exemption', models.FloatField()),
                ('round_down_to_nearest_10', models.BooleanField(default=True)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tax_rules', to='companies.Company')),
            ],
        ),
        migrations.CreateModel(
            name='TaxSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('salary_from', models.FloatField()),
                ('salary_to', models.FloatField(default=1000000000000)),
                ('tax_percentage', models.FloatField()),
                ('tax_discount_percentage', models.FloatField()),
                ('section_execution_sequence', models.IntegerField(default=0)),
                ('tax_rule_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='payroll.TaxRule')),
            ],
        ),
        migrations.AddField(
            model_name='salaryelement',
            name='type_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_elements', to='payroll.SalaryElementType'),
        ),
        migrations.AddField(
            model_name='salary',
            name='tax_rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='payroll.TaxRule'),
        ),
        migrations.AlterUniqueTogether(
            name='taxsection',
            unique_together=set([('name', 'tax_rule_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='taxrule',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='salaryelementtype',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='salaryelement',
            unique_together=set([('salary_id', 'type_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='salary',
            unique_together=set([('employee_id', 'year', 'month')]),
        ),
        migrations.AlterUniqueTogether(
            name='insurancerule',
            unique_together=set([('name', 'company_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='custompythonrule',
            unique_together=set([('name', 'company_id')]),
        ),
    ]
