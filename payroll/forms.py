from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.db.models import Q
from payroll.models import (Salary, SalaryElement, SalaryElementType,
                            InsuranceRule, TaxRule, TaxSection, CustomPythonRule)
from employees.models import Employee
from django.conf import settings as s
from datetime import datetime

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ('employee_id', 'year', 'month', 'basic_salary', 'variable_salary',
                  'insurance_rule', 'tax_rule', 'custom_rule')
        labels = {
            'employee_id': 'الموظف*',
            'year': 'السنة*',
            'month': 'الشهر*',
            'basic_salary': 'المرتب الاساسي*',
            'variable_salary': 'المرتب المتغير*',
            'insurance_rule': 'قاعدة التأمينات*',
            'tax_rule': 'قاعدة حساب الضريبة*',
            'custom_rule': 'قاعدة مخصصة',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد بيان مرتب لنفس الموظف فى النفس الشهر و السنة!",
                'not_latest':'يوجد بيان مرتب اخر أحدث من البيان الذى تحاول حفظة',
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].queryset = Employee.objects.filter(company_id=company_id)
        self.fields['insurance_rule'].queryset = InsuranceRule.objects.filter(Q(company_id=company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
        self.fields['tax_rule'].queryset = TaxRule.objects.filter(Q(company_id=company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
        self.fields['custom_rule'].queryset = CustomPythonRule.objects.filter(company_id=company_id)
        
# Salary Elements formset
labels = {
            'type_id': 'نوع البند*',
            'amount': 'المبلغ*',
        }

fields = '__all__'

SalaryElementFormSet = forms.inlineformset_factory(Salary, SalaryElement, fields=fields, labels=labels, extra=10)

class SalaryElementTypeForm(forms.ModelForm):
    class Meta:
        model = SalaryElementType
        fields = '__all__'
        labels = {
                'name': 'اسم البند*',
                'element_type': 'نوع البند*',
                'taxable': 'خاضع للضريبة'
            }
        widgets = {
                'company_id':forms.HiddenInput()
            }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد بند اخر مسجل بنفس الاسم!",
                }
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['element_type'].choices = [('', '---------'), ('addition', 'اضافة'), ('deduction', 'خصم')]

class InsuranceRuleForm(forms.ModelForm):
    class Meta:
        model = InsuranceRule
        fields = '__all__'
        labels = {
                'name': 'اسم القاعدة*',
                'basic_deduction_percentage': 'نسبة الخصم على الراتب الاساسي*',
                'variable_deduction_percentage': 'نسبة الخصم على الراتب المتغير*',
                'maximum_insurable_basic_salary':'الحد الأقصي للراتب الأساسي التأميني*',
                'maximum_insurable_variable_salary':'الحد الأقصي للراتب المتغير التأميني*'
            }
        widgets = {
                'company_id':forms.HiddenInput()
            }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد قاعدة أخري مسجلة بنفس الاسم!",
                }
            }

class CustomPythonRuleForm(forms.ModelForm):
    class Meta:
        model = CustomPythonRule
        exclude = ('help_text',)
        widgets = {
                'company_id':forms.HiddenInput(),
                'rule_definition':forms.Textarea(attrs={'style':'direction: ltr;font-family:"monospace";'})

            }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد قاعدة أخري مسجلة بنفس الاسم!",
                }
            }
        labels = {
            'name':'اسم القاعدة*',
            'rule_definition':'تعريف القاعدة بكود البايثون*',
            'taxable':'خاضعة للضريبة'
        }

class TaxRuleForm(forms.ModelForm):
    class Meta:
        model = TaxRule
        fields = '__all__'
        widgets = {
                'company_id':forms.HiddenInput()
            }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد قاعدة أخري مسجلة بنفس الاسم!",
                }
            }
        labels = {
            'name':'اسم القاعدة*',
            'personal_exemption':'قيمة الخصم الشخصي*',
            'round_down_to_nearest_10':'تقريب الرقم المحسوب الى أصغر 10',
        }

# Tax Sections formset
labels = {
            'name': 'اسم الشريحة*',
            'salary_from': 'من*',
            'salary_to': 'الي*',
            'tax_percentage': 'نسبة الضريبة*',
            'tax_discount_percentage': 'نسبة الخصم على الضريبة*',
            'section_execution_sequence':'ترتيب الشريحة فى الحساب*'
        }

fields = '__all__'

TaxSectionFormSet = forms.inlineformset_factory(TaxRule, TaxSection, fields=fields, labels=labels, extra=8)

class PayslipsForm(forms.Form):
    YEARS = [(y,y) for y in range(2000,2075)]
    MONTHS = [
        ('january','January'),('february','February'),('march','March'),('april','April'),
        ('may','May'),('june','June'),('july','July'),('august','August'),('september','September'),
        ('october','October'),('november','November'),('december','December')
    ]
    month = forms.ChoiceField(label='الشهر*', choices=MONTHS, initial=MONTHS[datetime.now().month-1][0])
    year = forms.ChoiceField(label='السنة*', choices=YEARS, initial=datetime.now().year)
    employee = forms.ModelChoiceField(queryset=None, label='الموظف*',empty_label='ارسال الي كل الموظفين', required=False)
    
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Employee.objects.filter(company_id=company_id)
        self.fields['employee'].queryset = queryset

class CopySalariesForm(forms.Form):
    YEARS = [(y,y) for y in range(2000,2075)]
    MONTHS = [
        ('january','January'),('february','February'),('march','March'),('april','April'),
        ('may','May'),('june','June'),('july','July'),('august','August'),('september','September'),
        ('october','October'),('november','November'),('december','December')
    ]
    from_month = forms.ChoiceField(label='نسخ من شهر*', choices=MONTHS, initial=MONTHS[datetime.now().month-2][0])
    from_year = forms.ChoiceField(label='و من سنة*', choices=YEARS, initial=datetime.now().year)
    to_month = forms.ChoiceField(label='الي شهر*', choices=MONTHS, initial=MONTHS[datetime.now().month-1][0])
    to_year = forms.ChoiceField(label='الي سنة*', choices=YEARS, initial=datetime.now().year)