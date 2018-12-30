from django.contrib import admin
from employees.models import Employee
from companies.models import (Company, Branch, Department, 
                              Section, SubSection, Degree)
from banks.models import BankAccount

# Inlines
class EmployeeInline(admin.TabularInline):
    model = Employee

class BranchInline(admin.TabularInline):
    model = Branch

class DepartmentInline(admin.TabularInline):
    model = Department

class SectionInline(admin.TabularInline):
    model = Section

class SubSectionInline(admin.TabularInline):
    model = SubSection

class DegreeInline(admin.TabularInline):
    model = Degree

class BankAccountInline(admin.TabularInline):
    model = BankAccount

# ModelAdmins
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        BranchInline,
        EmployeeInline,
        BankAccountInline,
    ]

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    inlines = [
        DepartmentInline,
        EmployeeInline,
    ]

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [
        SectionInline,
        EmployeeInline,
    ]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    inlines = [
        SubSectionInline,
        EmployeeInline,
    ]

@admin.register(SubSection)
class SubSectionAdmin(admin.ModelAdmin):
    inlines = [
        DegreeInline,
        EmployeeInline,
    ]

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]