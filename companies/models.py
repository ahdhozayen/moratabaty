from django.db import models

class Company(models.Model):
    class Meta:
        verbose_name_plural = 'Companies'

    name = models.CharField(max_length=255, unique=True)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name

class Branch(models.Model):
    class Meta:
        verbose_name_plural = 'Branches'
        unique_together = (('company_id','name'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='branches', on_delete=models.PROTECT)
    city_id = models.ForeignKey('countries.City', related_name='companies_branches', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + ">>" + self.company_id.name

class Department(models.Model):
    class Meta:
        unique_together = (('branch_id','name'))

    name = models.CharField(max_length=255)
    branch_id = models.ForeignKey('companies.Branch', related_name='departments', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + ">>" + str(self.branch_id)

class Section(models.Model):
    class Meta:
        unique_together = (('department_id','name'))

    name = models.CharField(max_length=255)
    department_id = models.ForeignKey('companies.Department', related_name='sections', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + ">>" + str(self.department_id)

class SubSection(models.Model):
    class Meta:
        unique_together = (('section_id','name'))

    name = models.CharField(max_length=255)
    section_id = models.ForeignKey('companies.Section', related_name='subsections', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + ">>" + str(self.section_id)

class Degree(models.Model):
    class Meta:
        unique_together = (('sub_section_id','name'))

    name = models.CharField(max_length=255)
    sub_section_id = models.ForeignKey('companies.SubSection', related_name='degrees', on_delete=models.PROTECT)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + ">>" + str(self.sub_section_id)
