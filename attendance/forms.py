from django import forms
from django.core.exceptions import NON_FIELD_ERRORS 
from attendance.models import Attendance, DayOffRule, DayOff
from employees.models import Employee

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ['department', 'section', 'sub_section', 'degree', 'total_attended_days', 'is_final']
        labels = {
            'employee_id': 'اسم الموظف*',
            'year': 'السنة*',
            'month':'الشهر*',
            'overtime_hours':'ساعات العمل الاضافية',
            'total_working_days_in_month':'أيام العمل فى هذا الشهر*',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد بيان حضور أخر لنفس الموظف فى نفس الشهر و السنة!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].queryset = Employee.objects.filter(company_id=company_id)

class DayOffRuleForm(forms.ModelForm):
    class Meta:
        model = DayOffRule
        fields = '__all__'
        labels = {
            'name': 'نوع الاجازة*',
            'salary_deduction_factor': 'معامل خصم المرتب*',
        }
        widgets = {
            'company_id':forms.HiddenInput()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد نوع اجازة اخر مسجل بنفس الاسم!",
            }
        }
# Day Offs formset
labels = {
            'rule_id': 'نوع الاجازة*',
            'number_of_days': 'عدد الايام*',
        }

fields = '__all__'

DayOffFormSet = forms.inlineformset_factory(Attendance, DayOff, fields=fields, labels=labels, extra=8)
