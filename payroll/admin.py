from django.contrib import admin
from payroll.models import (Salary, SalaryElementType, SalaryElement, 
                            InsuranceRule, TaxRule, TaxSection,
                            CustomPythonRule)

# Inlines
class SalaryElementInline(admin.TabularInline):
    model = SalaryElement

class TaxSectionInline(admin.TabularInline):
    model = TaxSection

# ModelAdmins
@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    readonly_fields = (
        'department',
        'section',
        'sub_section',
        'degree',
        'deducted_days',
        'total_untaxable_added_salary_elements',
        'total_taxable_added_salary_elements',
        'gross_salary',
        'total_untaxable_deducted_salary_elements',
        'total_taxable_deducted_salary_elements',
        'insurance_deduction',
        'abscense_days_deduction',
        'custom_rule_amount',
        'taxable_salary',
        'taxes_deduction',
        'net_salary',
    )
    
    inlines = [
        SalaryElementInline,
    ]

@admin.register(TaxRule)
class TaxRuleAdmin(admin.ModelAdmin):
    inlines = [
        TaxSectionInline,
    ]

@admin.register(CustomPythonRule)
class CustomPythonRuleAdmin(admin.ModelAdmin):
    readonly_fields = (
        'help_text',
    )

# Registering rest of models
admin.site.register([SalaryElementType, SalaryElement, InsuranceRule, TaxSection])
