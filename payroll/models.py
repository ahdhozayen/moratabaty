from django.db import models
from datetime import datetime
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from payroll.tax_calculator import TaxRule as TR

# fixed year and month range to be used later in payroll
YEARS = [(y,y) for y in range(2015,2050)]
MONTHS = [
    ('january','January'),('february','February'),('march','March'),('april','April'),
    ('may','May'),('june','June'),('july','July'),('august','August'),('september','September'),
    ('october','October'),('november','November'),('december','December')
]

class Salary(models.Model):
    class Meta:
        verbose_name_plural = 'Salaries'
        # unique constrain to check on the user salary in the same month and the same year.
        unique_together = (('employee_id','year','month'))

    employee_id = models.ForeignKey('employees.Employee', related_name='salaries', on_delete=models.PROTECT)
    is_final = models.BooleanField(default=False)

    # Information automatically acquired from employee chosen (Readonly fields)
    department = models.CharField(max_length=255, blank=True, null=True)
    section = models.CharField(max_length=255, blank=True, null=True)
    sub_section = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    deducted_days = models.FloatField()

    # Time info
    year = models.IntegerField(choices=YEARS, default=datetime.now().year)
    month = models.CharField(max_length=10, choices=MONTHS, default=MONTHS[datetime.now().month-1][0])
    date = models.DateField(blank=True, null=True)

    ## Salary info
    # main inputs
    basic_salary = models.FloatField()
    variable_salary = models.FloatField()
    # Insurance and Tax rules
    insurance_rule = models.ForeignKey('payroll.InsuranceRule', related_name='salaries', on_delete=models.PROTECT)
    tax_rule = models.ForeignKey('payroll.TaxRule', related_name='salaries', on_delete=models.PROTECT)
    # Custom rule
    custom_rule = models.ForeignKey('payroll.CustomPythonRule', related_name='salaries', blank=True, null=True, on_delete=models.PROTECT)
    # Calculated fields
    gross_salary = models.FloatField()
    total_untaxable_added_salary_elements = models.FloatField()
    total_taxable_added_salary_elements = models.FloatField()
    total_untaxable_deducted_salary_elements = models.FloatField()
    total_taxable_deducted_salary_elements = models.FloatField()
    insurance_deduction = models.FloatField()
    abscense_days_deduction = models.FloatField()
    custom_rule_amount = models.FloatField()
    taxable_salary = models.FloatField()
    taxes_deduction = models.FloatField()
    net_salary = models.FloatField()

    def _populate_employee_company_info(self):
        department = self.employee_id.department_id.name if self.employee_id.department_id else None
        section = self.employee_id.section_id.name if self.employee_id.section_id else None
        sub_section = self.employee_id.sub_section_id.name if self.employee_id.sub_section_id else None
        degree = self.employee_id.degree.name if self.employee_id.degree else None
        self.department = department
        self.section = section
        self.sub_section = sub_section
        self.degree = degree

    def populate_employee_deducted_days(self):
        total_deducted_days = 0
        attendance_recordset = self.employee_id.attendances.filter(year=self.year).filter(month=self.month)
        if len(attendance_recordset) > 0:
            attendance_record = attendance_recordset[0]
            day_offs = attendance_record.day_offs.all()
            if len(day_offs) > 0:
                for day in day_offs:
                    actual_days = day.number_of_days
                    deduction_factor = day.rule_id.salary_deduction_factor
                    days_to_deduct = actual_days * deduction_factor
                    total_deducted_days += days_to_deduct
        self.deducted_days = total_deducted_days

    def _populate_date_field(self):
            date_string = str(self.year) + '-' + self.month + '-' + '1'
            self.date = parse(date_string)

    def _get_untaxable_added_salary_elements_total(self):
        total_unataxable_added_salary_elements_amount = 0
        salary_elements_recordset = self.salary_elements.filter(type_id__element_type='addition').filter(type_id__taxable=False)
        for element in salary_elements_recordset:
            total_unataxable_added_salary_elements_amount += element.amount
        return total_unataxable_added_salary_elements_amount

    def _get_taxable_added_salary_elements_total(self):
        total_taxable_added_salary_elements_amount = 0
        salary_elements_recordset = self.salary_elements.filter(type_id__element_type='addition').filter(type_id__taxable=True)
        for element in salary_elements_recordset:
            total_taxable_added_salary_elements_amount += element.amount
        return total_taxable_added_salary_elements_amount

    def _get_untaxable_deducted_salary_elements_total(self):
        total_deducted_salary_elements_amount = 0
        salary_elements_recordset = self.salary_elements.filter(type_id__element_type='deduction').filter(type_id__taxable=False)
        for element in salary_elements_recordset:
            total_deducted_salary_elements_amount -= element.amount
        return -1 * total_deducted_salary_elements_amount

    def _get_taxable_deducted_salary_elements_total(self):
        total_deducted_salary_elements_amount = 0
        salary_elements_recordset = self.salary_elements.filter(type_id__element_type='deduction').filter(type_id__taxable=True)
        for element in salary_elements_recordset:
            total_deducted_salary_elements_amount -= element.amount
        return -1 * total_deducted_salary_elements_amount

    def _get_insurance_deduction(self):
        basic_deduction_ratio = self.insurance_rule.basic_deduction_percentage/100
        variable_deduction_ratio = self.insurance_rule.variable_deduction_percentage/100
        if self.basic_salary <= self.insurance_rule.maximum_insurable_basic_salary:
            basic_deduction = self.basic_salary * basic_deduction_ratio
        else:
            basic_deduction = self.insurance_rule.maximum_insurable_basic_salary * basic_deduction_ratio
        if self.variable_salary <= self.insurance_rule.maximum_insurable_variable_salary:
            variable_deduction = self.variable_salary * variable_deduction_ratio
        else:
            variable_deduction = self.insurance_rule.maximum_insurable_variable_salary * variable_deduction_ratio
        insurance_deduction = basic_deduction + variable_deduction
        return round(insurance_deduction, 2)

    def _get_deducted_days_deduction(self):
        employess_day_wage = (self.basic_salary + self.variable_salary)/30
        deducted_days_deduction = self.deducted_days * employess_day_wage
        return round(deducted_days_deduction, 2)

    def _get_gross_salary(self):
        return self.basic_salary + self.variable_salary + self.total_taxable_added_salary_elements + self.total_untaxable_added_salary_elements

    def _get_taxable_salary(self):
        if self.custom_rule:
            if self.custom_rule.taxable:
                custom_amount = self._get_custom_rule_amount()
            else:
                custom_amount = 0
        else:
            custom_amount = 0
        return (self.basic_salary + self.variable_salary + self.total_taxable_added_salary_elements - self.total_taxable_deducted_salary_elements -
                self.abscense_days_deduction - self.insurance_deduction + custom_amount)

    def _get_taxes_deduction(self):
        sections = self.tax_rule.sections.all()
        tax_rule = TR(self.tax_rule.personal_exemption, self.tax_rule.round_down_to_nearest_10)
        for section in sections:
            tax_rule.add_section(section.section_execution_sequence, section.salary_from, section.salary_to, section.tax_percentage, section.tax_discount_percentage)
        taxable_salary = self._get_taxable_salary()
        taxes = tax_rule.calculate_monthly_tax(taxable_salary)
        return round(taxes, 2)

    def _get_custom_rule_amount(self):
        if self.custom_rule == None:
            return 0
        # initials:
        basic = self.basic_salary
        variable = self.variable_salary
        d_days = self.deducted_days
        grs = self.gross_salary
        amount = 0
        custom_rule = self.custom_rule.rule_definition
        ldict = locals()
        exec(custom_rule, globals(), ldict)
        amount = ldict['amount']
        return amount

    def _populate_salary_fields(self):
        self.total_untaxable_added_salary_elements = self._get_untaxable_added_salary_elements_total()
        self.total_taxable_added_salary_elements = self._get_taxable_added_salary_elements_total()
        self.total_untaxable_deducted_salary_elements = self._get_untaxable_deducted_salary_elements_total()
        self.total_taxable_deducted_salary_elements = self._get_taxable_deducted_salary_elements_total()
        self.insurance_deduction = self._get_insurance_deduction()
        self.abscense_days_deduction = self._get_deducted_days_deduction()
        self.custom_rule_amount = self._get_custom_rule_amount()
        self.taxable_salary = self._get_taxable_salary()
        self.taxes_deduction = self._get_taxes_deduction()

    def _get_net_salary(self):
        if self.custom_rule:
            if self.custom_rule.taxable:
                custom_amount = 0
            else:
                custom_amount = self._get_custom_rule_amount()
        else:
            custom_amount = 0
        return (self.taxable_salary - self.taxes_deduction - self.total_untaxable_deducted_salary_elements
                + self.total_untaxable_added_salary_elements + custom_amount)

    def _freeze_attendance_if_final(self):
        if self.is_final:
            attendance_recordset = self.employee_id.attendances.filter(year=self.year).filter(month=self.month)
            if len(attendance_recordset) > 0:
                attendance_record = attendance_recordset[0]
                attendance_record.is_final = True
                attendance_record.save()

    def _validate_is_latest_record(self):
        later_records = Salary.objects.filter(date__gte=self.date).filter(employee_id=self.employee_id)
        if len(later_records) > 0:
            raise ValidationError('There is another Salary record that is later than this one', code='not_latest')

    def clean(self):
        self._populate_employee_company_info()
        self.populate_employee_deducted_days()
        self._populate_date_field()
        self._validate_is_latest_record()

    def save(self):
        self._populate_salary_fields()
        self.gross_salary = self._get_gross_salary()
        self.net_salary = self._get_net_salary()
        self._freeze_attendance_if_final()
        super().save()

    def __str__(self):
            return self.month + "/" + str(self.year) + "/" + self.employee_id.first_name + " " + self.employee_id.last_name

class SalaryElementType(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='salary_element_types', on_delete=models.PROTECT)
    element_type = models.CharField(max_length=255, choices=[('addition','Addition'),('deduction','Deduction')])
    taxable = models.BooleanField(default=False)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class SalaryElement(models.Model):
    class Meta:
        unique_together = (('salary_id', 'type_id' ))

    salary_id = models.ForeignKey('payroll.Salary', related_name='salary_elements', on_delete=models.PROTECT)
    type_id = models.ForeignKey('payroll.SalaryElementType', related_name='salary_elements', on_delete=models.PROTECT)
    amount = models.FloatField()

    def save(self):
        super().save()
        self.salary_id.save()

    def delete(self):
        super().delete()
        self.salary_id.save()

    def __str__(self):
        amount = str(self.amount)
        type_ = self.type_id.name
        employee = str(self.salary_id.employee_id)
        return amount + "/" + type_ + "/" + employee

class InsuranceRule(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='insurance_rules', on_delete=models.PROTECT)
    basic_deduction_percentage = models.FloatField()
    variable_deduction_percentage = models.FloatField()
    maximum_insurable_basic_salary = models.FloatField()
    maximum_insurable_variable_salary = models.FloatField()

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class TaxRule(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='tax_rules', on_delete=models.PROTECT)
    personal_exemption = models.FloatField()
    round_down_to_nearest_10 = models.BooleanField(default=True)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name

class TaxSection(models.Model):
    class Meta:
        unique_together = (('name', 'tax_rule_id'))

    name = models.CharField(max_length=255)
    tax_rule_id = models.ForeignKey('payroll.TaxRule', related_name='sections', on_delete=models.PROTECT)
    salary_from = models.FloatField()
    salary_to = models.FloatField(default=1000000000000)
    tax_percentage = models.FloatField()
    tax_discount_percentage = models.FloatField()
    section_execution_sequence = models.IntegerField(default=0)

    def clean(self):
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + str(self.tax_rule_id)

class CustomPythonRule(models.Model):
    class Meta:
        unique_together = (('name', 'company_id'))

    default_string = '''
    You can define a custom deduction/addition rule here using python code.
    You have the following variables available to use:
    * basic: this is the basic salary of the employee.
    * variable: this is the variable salary of the employee.
    * d_days: these are the number of days the employee should be deducted this month
    because of his/her absence or any other Attendance rules that implies deduction days.
    * grs:(without `o`) gross salary equals to basic salary + variable salary + any other added allowances/bonus/incentive etc..
    After calculating your equation, you have to store the required amount to be added/deducted in a variable named amount.
    If the value of the amount variable is positive, the amount will be added to the net salary of the employee.
    And if it is negative, it will be deducted.
    Example:
    if basic <= 5000:
    ____extra_deduction = -250
    else:
    ____extra_deduction = -500
    amount = extra_deduction
    Make Sure that your code is properly indented using 4 spaces
    '''
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey('companies.Company', related_name='custom_rules', on_delete=models.PROTECT)
    help_text = models.TextField(default=default_string)
    rule_definition = models.TextField()
    taxable = models.BooleanField(default=False)

    def _ensure_no_syntax_errors(self):
        basic = 0.0
        variable = 0.0
        d_days = 0.0
        grs = 0.0

        try:
            exec(self.rule_definition)
        except Exception as e:
            msg = 'The code You have wrote produced the following error:\n "{}"'.format(e)
            raise ValidationError(msg)

    def _validate_custom_rule_security(self):
        danger = [
            'im_class',	'im_func', '__func__', 'im_self', '__self__', '__dict__', '__class__', 'func_closure',
            '__closure__', 'func_code',	'__code__',	'func_defaults', '__defaults__', 'func_dict', 'func_doc',
            'func_globals',	'__globals__', 'func_name',	'gi_code', 'gi_frame', 'import', 'os', 'system',
            'subprocess', '__', 'class', 'print', 'eval', 'exec', 'popen', 'sys', '__builtins__', '__name__',
            '__package__', '__cached__', '__doc__', '__file__', '__loader__', '__spec__', 're', 'run', 'self',
            'compile', 'builtins', 'locals', 'globals', '__module__', 'object', '__base__', '__subclasses__',
            'type','Popen',
        ]
        for word in danger:
            if word in self.rule_definition:
                msg = 'FOR SECURITY REASONS, YOU ARE NOT ALLOWED TO USE "{}" IN YOUR CODE!!'.format(word)
                raise ValidationError(msg)

    def clean(self):
        self._validate_custom_rule_security()
        self._ensure_no_syntax_errors()
        self.name = self.name.capitalize()

    def __str__(self):
        return self.name + "/" + self.company_id.name
