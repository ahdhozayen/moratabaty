from django.db import models
from django.core.exceptions import ValidationError

class Bank(models.Model):
    class Meta:
        unique_together = (('name', 'branch', 'company_id'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='banks', on_delete=models.PROTECT)
    branch = models.CharField(max_length=255)
    address = models.TextField()
    transfer_from_account_id = models.ForeignKey('banks.BankAccount', on_delete=models.PROTECT, null=True, blank=True, related_name='transfer_to_bank')

    def clean(self):
        self.name = self.name.capitalize()
        self.branch = self.branch.capitalize()

    def __str__(self):
        return self.name + '/' + self.branch + '/' + self.company_id.name

class BankAccount(models.Model):
    class Meta:
        unique_together = (('account_number', 'bank_id'))

    bank_id = models.ForeignKey('banks.Bank', related_name='accounts', on_delete=models.PROTECT)
    account_type = models.CharField(max_length=20, choices=[('company','Company account'),('employee','Employee account')])
    currency_id = models.ForeignKey('banks.Currency', related_name='accounts', on_delete=models.PROTECT)
    account_number = models.CharField(max_length=255)
    account_employee_holder = models.OneToOneField('employees.Employee', related_name='bank_account', null=True, blank=True, on_delete=models.PROTECT)
    account_company_holder = models.ForeignKey('companies.Company', related_name='bank_accounts', null=True, blank=True, on_delete=models.PROTECT)

    def clean(self):
        try:
            employee_holder = self.account_employee_holder
        except:
            employee_holder = None
        try:
            company_holder = self.account_company_holder
        except:
            company_holder = None

        if self.account_type == 'company' and employee_holder:
            raise ValidationError('Holder of a company account cannot be an employee!', code='wrong_holder')
        elif self.account_type == 'employee' and company_holder:
            raise ValidationError('Holder of an employee account cannot be a company!', code='wrong_holder')
        elif not employee_holder and not company_holder:
            raise ValidationError('Please enter the holder of the account.', code='empty_holder')

    def __str__(self):
        return  self.account_number + '/' + str(self.bank_id)

class Currency(models.Model):
    class Meta:
        verbose_name_plural = 'Currencies'

    name = models.CharField(max_length=50, unique=True)

    def clean(self):
        self.name = self.name.upper()

    def __str__(self):
        return self.name
