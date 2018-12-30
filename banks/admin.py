from django.contrib import admin
from banks.models import Bank, BankAccount, Currency

# Inlines
class BankAccountInline(admin.TabularInline):
    model = BankAccount


# ModelAdmins
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    inlines = [
        BankAccountInline,
    ]

# Registering rest of models
admin.site.register([BankAccount, Currency])