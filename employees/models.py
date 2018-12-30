from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

VALID_IMG_EXTENSIONS = ['bmp', 'gif', 'png', 'ico', 'jpg', 'jpeg', 'psd']

class Employee(models.Model):
    class Meta:
        unique_together = (('id_number', 'company_id'), ('email', 'company_id'), ('employee_number', 'company_id'))

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=12, blank=True, default='')
    last_name = models.CharField(max_length=12, blank=True, default='')
    employee_number = models.IntegerField()
    email = models.EmailField(blank=True, null=True)
    picture = models.ImageField(null=True, blank=True, upload_to="img/users")
    is_active = models.BooleanField(blank=True, default=True)

    # Company Information
    company_id = models.ForeignKey('companies.Company', related_name='employees', on_delete=models.PROTECT)
    branch_id = models.ForeignKey('companies.Branch', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    department_id = models.ForeignKey('companies.Department', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    section_id = models.ForeignKey('companies.Section', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    sub_section_id = models.ForeignKey('companies.SubSection', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    degree = models.ForeignKey('companies.Degree', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    contract_type = models.ForeignKey('employees.Contract', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)

    # Personal Information
    id_type = models.ForeignKey('employees.IdDocument', related_name='employees', on_delete=models.PROTECT)
    id_number = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.ForeignKey('countries.City', related_name='born_in_employees', blank=True, null=True, on_delete=models.PROTECT)
    nationality = models.ForeignKey('countries.Nationality', related_name='citizen_employees', blank=True, null=True, on_delete=models.PROTECT)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    education_degree = models.ForeignKey('employees.EducationDegree', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    date_of_hiring = models.DateField(blank=True, null=True)
    gender = models.ForeignKey('employees.Gender', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    social_status = models.ForeignKey('employees.SocialStatus', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    military_status = models.ForeignKey('employees.MilitaryStatus', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)
    religion = models.ForeignKey('employees.Religion', related_name='employees', blank=True, null=True, on_delete=models.PROTECT)

    def _validate_image_extension(self):
        if self.picture:
            extension = self.picture.name.split('.')[-1]
            if extension not in VALID_IMG_EXTENSIONS:
                msg = "Only Files with the following extensions are allowed: 'bmp', 'gif', 'png', 'ico', 'jpg', 'jpeg', 'psd'"
                raise ValidationError(msg, code='wrong_extension')

    def clean(self):
        if self.user:
            if self.user.first_name:
                self.first_name = self.user.first_name
            if self.user.last_name:
                self.last_name = self.user.last_name
        elif not self.first_name:
            raise ValidationError('Please enter at least a first name for the Employee')
        self._validate_image_extension()

    def __str__(self):
            return self.first_name + " " + self.last_name + "/" + self.company_id.name

class Contract(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='contracts', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class IdDocument(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=20)
    company_id = models.ForeignKey('companies.Company', related_name='id_documents', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class EducationDegree(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='education_degrees', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class Gender(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='genders', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class SocialStatus(models.Model):
    class Meta:
        verbose_name_plural = 'Social status'
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='social_status', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class MilitaryStatus(models.Model):
    class Meta:
        verbose_name_plural = 'Military status'
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='military_status', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class Religion(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=12)
    company_id = models.ForeignKey('companies.Company', related_name='religions', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name
