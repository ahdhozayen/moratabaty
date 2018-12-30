from django import forms
from django.core.exceptions import NON_FIELD_ERRORS 
from banks.models import Bank, BankAccount
from employees.models import Employee

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = '__all__'
        labels = {
            'name': 'اسم البنك*',
            'branch': 'الفرع*',
            'address': 'العنوان*',
            'transfer_from_account_id':'رقم الحساب الذى يتم التحويل منه للبنك'
        }
        widgets = {
            'company_id':forms.HiddenInput()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد فرع اخر للبنك مسجل بنفس الاسم!",
            }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_from_account_id'].queryset = BankAccount.objects.filter(bank_id__company_id=company_id)

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'
        labels = {
            'bank_id':'البنك*',
            'account_type': 'نوع الحساب*',
            'currency_id': 'العملة*',
            'account_number':'رقم الحساب*',
            'account_employee_holder':'الموظف حامل الحساب*',
        }
        widgets = {
            'account_company_holder':forms.HiddenInput()
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "يوجد حساب اخر للبنك مسجل بنفس الرقم!",
                'empty_holder':'يجب أن تقوم بادخال حامل الحساب',
                'wrong_holder':'لا يمكن أن يكون حامل حساب الشركة موظف او العكس!'
            },
        
            'account_employee_holder':{
                'unique':'يوجد حساب مسجل اخر لنفس الموظف!',
                }
        }
    def __init__(self, company_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_id'].queryset = Bank.objects.filter(company_id=company_id)
        self.fields['account_employee_holder'].queryset = Employee.objects.filter(company_id=company_id)
        self.fields['account_type'].choices = [('', '---------'), ('company', 'حساب للشركة'), ('employee', 'حساب موظف')]
