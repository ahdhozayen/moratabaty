from django.db import models
from datetime import datetime

YEARS = [(y,y) for y in range(2015,2050)]
MONTHS = [
    ('january','January'),('february','February'),('march','March'),('april','April'),
    ('may','May'),('june','June'),('july','July'),('august','August'),('september','September'),
    ('october','October'),('november','November'),('december','December')
]

class Attendance(models.Model):
    class Meta:
        unique_together = (('employee_id','year','month'))

    employee_id = models.ForeignKey('employees.Employee', related_name='attendances', on_delete=models.PROTECT)
    is_final = models.BooleanField(default=False)

    # Information automatically acquired from employee chosen
    department = models.CharField(max_length=255, blank=True, null=True)
    section = models.CharField(max_length=255, blank=True, null=True)
    sub_section = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)

    # Time info
    year = models.IntegerField(choices=YEARS, default=datetime.now().year)
    month = models.CharField(max_length=10, choices=MONTHS, default=MONTHS[datetime.now().month-1][0])

    # Attendance info
    overtime_hours = models.FloatField(blank=True, null=True)
    total_working_days_in_month = models.IntegerField()
    total_attended_days = models.FloatField()

    def clean(self):
        department = self.employee_id.department_id.name if self.employee_id.department_id else None
        section = self.employee_id.section_id.name if self.employee_id.section_id else None
        sub_section = self.employee_id.sub_section_id.name if self.employee_id.sub_section_id else None
        degree = self.employee_id.degree.name if self.employee_id.degree else None

        self.department = department
        self.section = section
        self.sub_section = sub_section
        self.degree = degree

    def save(self):
        total_day_offs = 0
        day_off_recordset = self.day_offs.all()
        for d in day_off_recordset:
            total_day_offs += d.number_of_days
        self.total_attended_days = self.total_working_days_in_month - total_day_offs
        super().save()

    def __str__(self):
        return self.month + "/" + str(self.year) + "/" + self.employee_id.first_name + " " + self.employee_id.last_name

class DayOffRule(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='day_off_rules', on_delete=models.PROTECT)
    salary_deduction_factor = models.FloatField()

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class DayOff(models.Model):
    attendance_id = models.ForeignKey('attendance.Attendance', related_name='day_offs', on_delete=models.PROTECT)
    rule_id = models.ForeignKey('attendance.DayOffRule', related_name='day_offs', on_delete=models.PROTECT)
    number_of_days = models.FloatField()

    def save(self):
        super().save()
        self.attendance_id.save()

    def delete(self):
        super().delete()
        self.attendance_id.save()

    def __str__(self):
        days = str(self.number_of_days)
        rule = self.rule_id.name
        employee = str(self.attendance_id.employee_id)
        return days + "/" + rule + "/" + employee
