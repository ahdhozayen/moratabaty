from import_export import resources
from employees.models import Employee

#  helper class to help with the upload file data function.
class EmployeeResources(resources.ModelResource):
    class Meta:
        model = Employee
