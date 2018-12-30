from django.contrib import admin
from countries.models import (Country, City, Nationality)
from companies.models import Branch
from employees.models import Employee

# Inlines
class EmployeeInline(admin.TabularInline):
    model = Employee

class CityInline(admin.TabularInline):
    model = City

class NationalityInline(admin.TabularInline):
    model = Nationality

class BranchInline(admin.TabularInline):
    model = Branch

# ModelAdmins
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    inlines = [
        CityInline,
        NationalityInline,
    ]

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    inlines = [
        BranchInline,
        EmployeeInline,
    ]

@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]
