from django import forms
from django.core.exceptions import NON_FIELD_ERRORS 
from companies.models import Degree
from employees.models import (Employee, Contract, IdDocument,
                              EducationDegree, Gender, SocialStatus,
                              MilitaryStatus, Religion)

class EmployeeForm(forms.ModelForm):
    user_name = forms.CharField(label='اسم المستخدم',required=False)
    password = forms.CharField(label='كلمة السر', widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Employee
        exclude = ['user', 'branch_id', 'department_id', 'section_id','sub_section_id', 'is_active']
        widgets = {
            'company_id':forms.HiddenInput(),
            'date_of_birth':forms.SelectDateWidget(years=list(range(1930,2040)), empty_label=('السنة','الشهر','اليوم')),
            'date_of_hiring':forms.SelectDateWidget(years=list(range(1975,2075)), empty_label=('السنة','الشهر','اليوم')),
            'picture':forms.FileInput(attrs={'class':'btn btn-link', 'style':'box-shadow:none;margin-right:10px'})

        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد موظف اخر بنفس رقم وثيقة الهوية أو نفس البريد الالكتروني!",
                'wrong_extension': "ملف الصورة يجب أن يكون واحد من هذة الأنواع فقط: 'bmp', 'gif', 'png', 'ico', 'jpg', 'jpeg', 'psd'"
            }
        }
        labels = {
            'first_name': 'الاسم الاول*',
            'last_name': 'الاسم الثانى',
            'employee_number': 'رقم الموظف*',
            'email':'البريد الالكتروني',
            'picture':'الصورة ',
            'degree':'بيانات الوظيفة:  الدرجة>>الوظيفة>>القسم>>الادارة>>الفرع>>الشركة',
            'contract_type':'نوع التعاقد',
            'id_type':'نوع وثيقة الهوية*',
            'id_number':'رقم وثيقة الهوية*',
            'date_of_birth':'تاريخ الميلاد',
            'place_of_birth':'محل الميلاد',
            'nationality':'الجنسية',
            'field_of_study':'مجال الدراسة',
            'education_degree':'الدرجة التعليمية',
            'date_of_hiring':'تاريخ التعيين',
            'gender':'النوع',
            'social_status':'الحالة الاجتماعية',
            'military_status':'الموقف من التجنيد',
            'religion':'الديانة',
        }

    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['degree'].queryset = Degree.objects.filter(
            sub_section_id__section_id__department_id__branch_id__company_id=company_id)
        self.fields['contract_type'].queryset = Contract.objects.filter(company_id=company_id)
        self.fields['id_type'].queryset = IdDocument.objects.filter(company_id=company_id)
        self.fields['education_degree'].queryset = EducationDegree.objects.filter(company_id=company_id)
        self.fields['gender'].queryset = Gender.objects.filter(company_id=company_id)
        self.fields['social_status'].queryset = SocialStatus.objects.filter(company_id=company_id)
        self.fields['military_status'].queryset = MilitaryStatus.objects.filter(company_id=company_id)
        self.fields['religion'].queryset = Religion.objects.filter(company_id=company_id)

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد عقد اخر بنفس الاسم!",
            }
        }
        labels = {
            'name': 'اسم العقد*',
    }

class IdDocumentForm(forms.ModelForm):
    class Meta:
        model = IdDocument
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد وثيقة هوية اخري بنفس الاسم!",
            }
        }
        labels = {
            'name': 'اسم وثيقة الهوية*',
        }

class EducationDegreeForm(forms.ModelForm):
    class Meta:
        model = EducationDegree
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد درجة تعليمية اخري بنفس الاسم!",
            }
        }
        labels = {
            'name': 'اسم الدرجة التعليمية*',
        }

class GenderForm(forms.ModelForm):
    class Meta:
        model = Gender
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد نوع اخر بنفس الاسم!",
            }
        }
        labels = {
            'name': 'نوع أو جنس الموظف*',
        }

class SocialStatusForm(forms.ModelForm):
    class Meta:
        model = SocialStatus
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد حالة اجتماعية اخري بنفس الاسم!",
            }
        }
        labels = {
            'name': 'اسم الحالة الاجتماعية*',
        }

class MilitaryStatusForm(forms.ModelForm):
    class Meta:
        model = MilitaryStatus
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد موقف من التجنيد اخر بنفس الاسم!",
            }
        }
        labels = {
            'name': 'اسم الموقف من التجنيد*',
        }

class ReligionForm(forms.ModelForm):
    class Meta:
        model = Religion
        fields = '__all__'
        widgets = {
            'company_id':forms.HiddenInput(),
        }        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد ديانة اخري مسجلة بنفس الاسم",
            }
        }
        labels = {
            'name': 'اسم الديانة*',
        }