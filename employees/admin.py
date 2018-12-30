from django.contrib import admin
from employees.models import (Employee, Contract, IdDocument,
                              EducationDegree, Gender, SocialStatus,
                              MilitaryStatus, Religion)
from attendance.models import Attendance
from payroll.models import Salary
from banks.models import BankAccount
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User

# Inlines
class EmployeeInline(admin.TabularInline):
    model = Employee

class AttendanceInline(admin.TabularInline):
    model = Attendance

class SalaryInline(admin.TabularInline):
    model = Salary

class BankAccountInline(admin.TabularInline):
    model = BankAccount

# ModelAdmins
@admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     inlines = [
#         AttendanceInline,
#         SalaryInline,
#         BankAccountInline,
#     ]
class EmployeeAdmin(ImportExportModelAdmin):
    inlines = [
        AttendanceInline,
        SalaryInline,
        BankAccountInline,
    ]

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(IdDocument)
class IdDocumentAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(EducationDegree)
class EducationDegreeAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(SocialStatus)
class SocialStatusAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(MilitaryStatus)
class MilitaryStatusAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]
