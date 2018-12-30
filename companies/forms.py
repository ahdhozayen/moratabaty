from django import forms
from django.core.exceptions import NON_FIELD_ERRORS 
from companies.models import Company, Branch, Department, Section, SubSection, Degree

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'name': 'اسم الشركة*',
        }
        error_messages = {
            'name': {
                'unique': "هذا الاسم مستخدم من قبل، برجاء اختيار اسم اخر",
            }
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'
        labels = {
            'name': 'اسم الفرع*',
            'city_id': 'المدينة*',
        }
        widgets = {
            'company_id':forms.HiddenInput()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد فرع اخر مسجل بنفس الاسم!",
            }
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        labels = {
            'name': 'اسم الادارة*',
            'branch_id': 'الفرع*',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد ادارة اخرى بنفس الاسم مسجلة على نفس الفرع!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch_id'].queryset = Branch.objects.filter(company_id=company_id)
        
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'
        labels = {
            'name': 'اسم القسم*',
            'department_id': 'الادارة*',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد قسم اخر بنفس الاسم مسجل على نفس الادارة!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department_id'].queryset = Department.objects.filter(branch_id__company_id=company_id)

class SubSectionForm(forms.ModelForm):
    class Meta:
        model = SubSection
        fields = '__all__'
        labels = {
            'name': 'اسم الوظيفة*',
            'section_id': 'القسم*',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد وظيفة اخرى بنفس الاسم مسجلة على نفس القسم!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_id'].queryset = Section.objects.filter(department_id__branch_id__company_id=company_id)

class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = '__all__'
        labels = {
            'name': 'اسم الدرجة*',
            'sub_section_id': 'الوظيفة*',
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "توجد درجة اخرى بنفس الاسم مسجلة على نفس الوظيفة!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_section_id'].queryset = SubSection.objects.filter(section_id__department_id__branch_id__company_id=company_id)
        