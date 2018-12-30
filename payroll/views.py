from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings as s
from payroll.pdf_email_helper import Mailer
from payroll.sending_report import SendingReport
from payroll.models import Salary, SalaryElementType, InsuranceRule, CustomPythonRule, TaxRule
from payroll.forms import (SalaryForm, SalaryElementFormSet, SalaryElementTypeForm, InsuranceRuleForm,
                           CustomPythonRuleForm, TaxRuleForm, TaxSectionFormSet, PayslipsForm, CopySalariesForm)
from employees.models import Employee
from pdfkit import from_string as convert_to_pdf
from time import sleep
from threading import Thread
import os
from django.http import HttpResponseForbidden

@login_required
def salaries_list(request, by):
    context = {'table_title':'المرتبات', 'modal_title':'اضافة بيان مرتب جديد', 'formset_title':'بنود اضافية'}
    if request.method == "POST":
        form = SalaryForm(request.user.employee.company_id, request.POST)
        formset = SalaryElementFormSet(request.POST)
        formset.can_delete = False
        formset_queryset = SalaryElementType.objects.filter(company_id=request.user.employee.company_id)
        for f in formset.forms:
            f.fields['type_id'].queryset=formset_queryset
        if form.is_valid():
            salary = form.save(commit=False)
            formset = SalaryElementFormSet(request.POST, instance=salary)
            formset.can_delete = False
            for f in formset.forms:
                f.fields['type_id'].queryset=formset_queryset
            if formset.is_valid():
                salary.save()
                formset.save()
                success_msg = 'تم اضافة "{}" بنجاح'.format(str(salary))
                messages.success(request, success_msg)
                # Emptying the form and formset before rerendering them back
                form = SalaryForm(request.user.employee.company_id)
                formset = SalaryElementFormSet()
                formset.can_delete = False
                for f in formset.forms:
                    f.fields['type_id'].queryset=formset_queryset
            else: # formset was not valid
                for error_dict in formset.errors:
                    [messages.error(request, error[0]) for error in error_dict.values()]
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context['save_and_add'] = save_and_add
    else:   # Request is GET
        try:
            # Just passing empty form and formset to be rendered in case of GET
            form = SalaryForm(request.user.employee.company_id)
            formset = SalaryElementFormSet()
            formset.can_delete = False
            formset_queryset = SalaryElementType.objects.filter(company_id=request.user.employee.company_id)
            for f in formset.forms:
                f.fields['type_id'].queryset=formset_queryset
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'payroll/salaries_list.html')
    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
    if by != '':
        salaries = Salary.objects.filter(employee_id__company_id=request.user.employee.company_id).order_by(by)
    else:
        salaries = Salary.objects.filter(employee_id__company_id=request.user.employee.company_id)
    context['salaries'] = salaries
    context['form'] = form
    context['formset'] = formset
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'payroll/salaries_list.html', context=context)

@login_required
def delete_salary(request, pk):
    try:
        salary = Salary.objects.get(pk=pk)
        if salary.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if salary.is_final:
            messages.error(request, 'هذا البيان نهائي و لا يمكن حذفة!')
            return redirect('payroll:salaries_list', by='')
        salary.delete()
        success_msg = 'تم حذف "{}" بنجاح'.format(str(salary))
        messages.success(request, success_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:salaries_list', by='')

@login_required
def edit_salary(request, pk):
    try:
        salary = Salary.objects.get(pk=pk)
        if salary.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if salary.is_final:
            messages.error(request, 'هذا البيان نهائي و لا يمكن تعديلة!')
            return redirect('payroll:salaries_list', by='')
        formset_queryset = SalaryElementType.objects.filter(company_id=request.user.employee.company_id)
        context = {'table_title':'المرتبات', 'modal_title':'تعديل بيان المرتب', 'formset_title':'بنود المرتب'}
        if request.method == 'POST':
            form = SalaryForm(request.user.employee.company_id, request.POST, instance=salary)
            formset = SalaryElementFormSet(request.POST, instance=salary)
            for f in formset.forms:
                f.fields['type_id'].queryset=formset_queryset
                f.fields['DELETE'].label = 'حذف'
            if form.is_valid() and formset.is_valid():
                salary = form.save()
                formset.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(str(salary))
                messages.success(request, success_msg)
            else: # Form or/and formset were not valid
                # Spitting the errors coming from the form and formset
                [messages.error(request, error[0]) for error in form.errors.values()]
                for error_dict in formset.errors:
                    [messages.error(request, error[0]) for error in error_dict.values()]
        else: # request method is GET
            form = SalaryForm(request.user.employee.company_id, instance=salary)
            formset = SalaryElementFormSet(instance=salary)
            for f in formset.forms:
                f.fields['type_id'].queryset=formset_queryset
                f.fields['DELETE'].label = 'حذف'
            modal_close_url = 'payroll:salaries_list'
            context['modal_close_url'] = modal_close_url
            context['editing'] = True
            try:
                salaries = Salary.objects.filter(employee_id__company_id=request.user.employee.company_id)
                context['salaries'] = salaries
                context['form'] = form
                context['formset'] = formset
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'payroll/salaries_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('payroll:salaries_list', by='')

@login_required
def finalize_salary(request, pk):
    try:
        salary = Salary.objects.get(pk=pk)
        if salary.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        salary.is_final = True
        salary.save()
        success_msg = 'البيان {} أصبح الان نسخة نهائية'.format(str(salary))
        messages.success(request, success_msg)
    except:
        error_msg = 'لم يتم التعديل المطلوب، خطأ ما قد حدث'
    return redirect('payroll:salaries_list', by='')

@login_required
def recalculate_salary(request, pk):
    try:
        salary = Salary.objects.get(pk=pk)
        if salary.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if salary.is_final:
            error_msg = 'هذا البيان نهائي و لا يمكن تعديلة!'
            messages.error(request, error_msg)
            return redirect('payroll:salaries_list', by='')
        salary.populate_employee_deducted_days()
        salary.save()
        success_msg = 'تم اعادة حساب و تحديث البيان "{}" بنجاح'.format(str(salary))
        messages.success(request, success_msg)
    except:
        error_msg = 'لم يتم التحديث المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:salaries_list', by='')

@login_required
def copy_salaries(request):
    if request.method == 'POST':
        form = CopySalariesForm(request.POST)
        if form.is_valid():
            from_month = form.cleaned_data['from_month']
            from_year = form.cleaned_data['from_year']
            to_month = form.cleaned_data['to_month']
            to_year = form.cleaned_data['to_year']

            salaries = Salary.objects.filter(year=from_year).filter(month=from_month)
            successes = 0
            failures = 0
            for salary in salaries:
                salary.pk = None
                salary.month = to_month
                salary.year = to_year
                salary.is_final = False
                try:
                    salary.clean()                    
                    salary.save()
                    successes += 1
                except:
                    failures += 1
            success_msg = "تم نسخ عدد {} بيانات مرتبات بنجاح".format(successes)
            failure_msg = "لم يتم نسخ عدد {}".format(failures)
            messages.success(request, success_msg)
            messages.error(request, failure_msg)
            return redirect('payroll:salaries_list', by='')
        else: # Form was not valid
            [messages.error(request, error[0]) for error in form.errors.values()]
            form = CopySalariesForm()
    else: # Method is Get
        form = CopySalariesForm()
    context = {'form':form}
    return render(request, 'payroll/copy_salaries.html', context=context)

@login_required
def send_payslips(request):
    if request.method == 'POST':
        form = PayslipsForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            employee = form.cleaned_data['employee'] if form.cleaned_data['employee'] else 'all'
            sending_reports = _send_emails(employee, month, year, request.user.employee.company_id)
            return render(request, 'payroll/payslips_sending_reports.html', context={'sending_reports':sending_reports})
    else:
        form = PayslipsForm(request.user.employee.company_id)
    context = {'form':form}
    return render(request, 'payroll/payslips_sending_form.html', context=context)

def _send_emails(employee: Employee, month, year, company_id):
    if employee == 'all':
        employees = Employee.objects.filter(company_id=company_id)
    else: 
        employees = [employee,]
    mailer = Mailer(s.ADMIN_EMAIL, s.ADMIN_EMAIL_PASS)
    msg_body = r'''
    Dear {}
    Kindly find attached your payslip for {} - {}
    Thanks and best regards
    '''
    junk_files = []
    sending_reports = []
    for employee in employees:
        employee_number = employee.employee_number
        name = employee.first_name + " " + employee.last_name
        email = employee.email
        sending_report = SendingReport(employee_number, name, email)
        if employee.is_active:
            if employee.email:
                salary = employee.salaries.filter(year=year).filter(month=month)
                if len(salary) > 0:
                    salary = salary[0]
                    file_path, file_name = _create_payslip_pdf(salary)
                    formatted_msg_body = msg_body.format(salary.employee_id.first_name, salary.month, salary.year)
                    user_email = salary.employee_id.email
                    msg = mailer.create_msg(user_email, 'Your Payslip is Ready!', formatted_msg_body, file_path=file_path, file_name=file_name)
                    mailer.send_mail(msg)
                    sending_report.status = 'success'
                    sending_report.reason = ''
                    sending_reports.append(sending_report)
                    junk_files.append(file_path)
                else:
                    sending_report.status = 'fail'
                    sending_report.reason = 'الموظف ليس لديه بيان مرتب فى الفترة التى تم تحديدها'
                    sending_reports.append(sending_report)
            else:
                sending_report.status = 'fail'
                sending_report.reason = 'الموظف ليس لدية بريد الكتروني مسجل'
                sending_reports.append(sending_report)
        else:
            sending_report.status = 'fail'
            sending_report.reason = 'الموظف تم ايقافة'
            sending_reports.append(sending_report)
    mailer.join_all_threads()
    t = Thread(target=_delete_pdf_files, args=(junk_files,))
    t.start()
    return sending_reports

def _create_payslip_pdf(salary):
    data_dict = _prepare_payslip_data(salary)
    template_path = os.path.join(s.BASE_DIR,'payroll','templates','payroll','emails','payslip.html')
    f = open(template_path, 'r', encoding='UTF-8')
    source_html = f.read().format(**data_dict)
    f.close()
    # We will use the `pk.pdf` naming format to avoid encoding problems of arabic letters in the wkhtmltopdf library
    initial_output_file_name = str(salary.employee_id.pk) + '.pdf'
    initial_output_file_path = os.path.join(s.BASE_DIR,'payroll','temporary_payslips', initial_output_file_name)
    convert_to_pdf(source_html, initial_output_file_path)
    # After converting the payslip to pdf, we can now freely rename the file to whatever we want before sending it
    final_output_file_name = salary.employee_id.first_name + '-' + salary.month + '-' + str(salary.year) + '-' + salary.employee_id.company_id.name + str(salary.employee_id.pk) + '.pdf'
    final_output_file_path = os.path.join(s.BASE_DIR,'payroll','temporary_payslips', final_output_file_name)
    os.rename(initial_output_file_path, final_output_file_path)
    return [final_output_file_path, final_output_file_name]

def _prepare_payslip_data(salary: Salary):
    data = {}
    data['salary'] = str(salary)
    data['slip_status'] = 'نهائية' if salary.is_final else 'غير نهائية'
    data['first_name'] = salary.employee_id.first_name
    data['last_name'] = salary.employee_id.last_name
    data['month'] = salary.month
    data['year'] = salary.year
    data['department'] = salary.department
    data['section'] = salary.section
    data['sub_section'] = salary.sub_section
    data['degree'] = salary.degree
    data['basic_salary'] = salary.basic_salary
    data['variable_salary'] = salary.variable_salary
    data['deducted_days'] = salary.deducted_days
    data['abscense_days_deduction'] = salary.abscense_days_deduction
    data['total_untaxable_added_salary_elements'] = salary.total_untaxable_added_salary_elements
    data['total_taxable_added_salary_elements'] = salary.total_taxable_added_salary_elements
    data['gross_salary'] = salary.gross_salary
    data['total_untaxable_deducted_salary_elements'] = salary.total_untaxable_deducted_salary_elements
    data['total_taxable_deducted_salary_elements'] = salary.total_taxable_deducted_salary_elements
    data['insurance_deduction'] = salary.insurance_deduction
    data['taxable_salary'] = salary.taxable_salary
    data['taxes_deduction'] = salary.taxes_deduction
    data['custom_rule_amount'] = salary.custom_rule_amount
    data['net_salary'] = salary.net_salary

    return data

def _delete_pdf_files(files):
    sleep(60)
    for file in files:
        os.remove(file)

@login_required
def salary_element_types_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = SalaryElementTypeForm(request.POST)
        if form.is_valid():
            salary_element_type = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(salary_element_type.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = SalaryElementTypeForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'أنواع بنود المرتب', 'modal_title':'اضافة نوع بند جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = SalaryElementTypeForm()
        context = {'table_title':'أنواع بنود المرتب', 'modal_title':'اضافة نوع بند جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            salary_element_types = SalaryElementType.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            salary_element_types = SalaryElementType.objects.filter(company_id=request.user.employee.company_id)
        context['salary_element_types'] = salary_element_types
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'payroll/salary_element_types_list.html', context=context)

@login_required
def delete_salary_element_type(request, pk):
    try:
        salary_element_type = SalaryElementType.objects.get(pk=pk)
        if salary_element_type.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(salary_element_type.salary_elements.all()) == 0:
            salary_element_type.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(salary_element_type.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(salary_element_type.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:salary_element_types_list', by='')

@login_required
def edit_salary_element_type(request, pk):
    try:
        salary_element_type = SalaryElementType.objects.get(pk=pk)
        if salary_element_type.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = SalaryElementTypeForm(request.POST, instance=salary_element_type)
            if form.is_valid():
                salary_element_type = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(salary_element_type.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = SalaryElementTypeForm(instance=salary_element_type)
            modal_close_url = 'payroll:salary_element_types_list'
            context = {'table_title': 'أنواع بنود المرتب', 'modal_title':'تعديل البند', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                salary_element_types = SalaryElementType.objects.filter(company_id=request.user.employee.company_id)
                context['salary_element_types'] = salary_element_types
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'payroll/salary_element_types_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('payroll:salary_element_types_list', by='')

@login_required
def insurance_rules_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = InsuranceRuleForm(request.POST)
        if form.is_valid():
            insurance_rule = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(insurance_rule.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = InsuranceRuleForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'قواعد احتساب التأمينات', 'modal_title':'اضافة قاعدة جديدة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = InsuranceRuleForm()
        context = {'table_title':'قواعد احتساب التأمينات', 'modal_title':'اضافة قاعدة جديدة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            insurance_rules = InsuranceRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME)).order_by(by)
        else:
            insurance_rules = InsuranceRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
        context['insurance_rules'] = insurance_rules
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'payroll/insurance_rules_list.html', context=context)

@login_required
def delete_insurance_rule(request, pk):
    try:
        insurance_rule = InsuranceRule.objects.get(pk=pk)
        if insurance_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if insurance_rule.company_id.name == s.SPECIAL_COMPANY_NAME:
            messages.error(request, 'هذا البيان غير قابل للحذف!!')
            return redirect('payroll:insurance_rules_list', by='')
        elif len(insurance_rule.salaries.all()) == 0:
            insurance_rule.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(insurance_rule.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(insurance_rule.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:insurance_rules_list', by='')

@login_required
def edit_insurance_rule(request, pk):
    try:
        insurance_rule = InsuranceRule.objects.get(pk=pk)
        if insurance_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if insurance_rule.company_id.name == s.SPECIAL_COMPANY_NAME:
            messages.error(request, 'هذا البيان غير قابل للتعديل!!')
            return redirect('payroll:insurance_rules_list', by='')
        elif request.method == 'POST':
            form = InsuranceRuleForm(request.POST, instance=insurance_rule)
            if form.is_valid():
                insurance_rule = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(insurance_rule.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = InsuranceRuleForm(instance=insurance_rule)
            modal_close_url = 'payroll:insurance_rules_list'
            context = {'table_title': 'قواعد احتساب التأمينات', 'modal_title':'تعديل القاعدة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                insurance_rules = InsuranceRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
                context['insurance_rules'] = insurance_rules
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'payroll/insurance_rules_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('payroll:insurance_rules_list', by='')

@login_required
def custom_rules_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = CustomPythonRuleForm(request.POST)
        if form.is_valid():
            custom_rule = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(custom_rule.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = CustomPythonRuleForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'قواعد الاحتساب المخصصة', 'modal_title':'اضافة قاعدة جديدة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = CustomPythonRuleForm()
        context = {'table_title':'قواعد الاحتساب المخصصة', 'modal_title':'اضافة قاعدة جديدة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            custom_rules = CustomPythonRule.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            custom_rules = CustomPythonRule.objects.filter(company_id=request.user.employee.company_id)
        context['custom_rules'] = custom_rules
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'payroll/custom_rules_list.html', context=context)

@login_required
def delete_custom_rule(request, pk):
    try:
        custom_rule = CustomPythonRule.objects.get(pk=pk)
        if custom_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(custom_rule.salaries.all()) == 0:
            custom_rule.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(custom_rule.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(custom_rule.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:custom_rules_list', by='')

@login_required
def edit_custom_rule(request, pk):
    try:
        custom_rule = CustomPythonRule.objects.get(pk=pk)
        if custom_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = CustomPythonRuleForm(request.POST, instance=custom_rule)
            if form.is_valid():
                custom_rule = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(custom_rule.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = CustomPythonRuleForm(instance=custom_rule)
            modal_close_url = 'payroll:custom_rules_list'
            context = {'table_title': 'قواعد الاحتساب المخصصة', 'modal_title':'تعديل القاعدة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                custom_rules = CustomPythonRule.objects.filter(company_id=request.user.employee.company_id)
                context['custom_rules'] = custom_rules
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'payroll/custom_rules_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('payroll:custom_rules_list', by='')

@login_required
def tax_rules_list(request, by):
    context = {'table_title':'قواعد احتساب الضريبة', 'modal_title':'اضافة قاعدة جديدة', 'formset_title':'شرائح احتساب الضريبة'}
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = TaxRuleForm(request.POST)
        formset = TaxSectionFormSet(request.POST)
        formset.can_delete = False
        if form.is_valid():
            tax_rule = form.save(commit=False)
            formset = TaxSectionFormSet(request.POST, instance=tax_rule)
            formset.can_delete = False
            if formset.is_valid():
                tax_rule.save()
                formset.save()
                success_msg = 'تم اضافة "{}" بنجاح'.format(tax_rule.name)
                messages.success(request, success_msg)
                # Emptying the form and formset before rerendering them back
                form = TaxRuleForm()
                formset = TaxSectionFormSet()
                formset.can_delete = False
            else: # formset was not valid
                for error_dict in formset.errors:
                    [messages.error(request, error[0]) for error in error_dict.values()]
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context['save_and_add'] = save_and_add
    else:   # Request is GET
        try:
            # Just passing empty form and formset to be rendered in case of GET
            form = TaxRuleForm()
            formset = TaxSectionFormSet()
            formset.can_delete = False
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'payroll/tax_rules_list.html')
    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
    if by != '':
        tax_rules = TaxRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME)).order_by(by)
    else:
        tax_rules = TaxRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
    context['tax_rules'] = tax_rules
    context['form'] = form
    context['formset'] = formset
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'payroll/tax_rules_list.html', context=context)

@login_required
def delete_tax_rule(request, pk):
    try:
        tax_rule = TaxRule.objects.get(pk=pk)
        if tax_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if tax_rule.company_id.name == s.SPECIAL_COMPANY_NAME:
            messages.error(request, 'هذا البيان غير قابل للحذف!!')
            return redirect('payroll:tax_rules_list', by='')
        elif len(tax_rule.salaries.all()) == 0:
            tax_rule.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(tax_rule.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(tax_rule.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('payroll:tax_rules_list', by='')

@login_required
def edit_tax_rule(request, pk):
    try:
        tax_rule = TaxRule.objects.get(pk=pk)
        if tax_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        context = {'table_title':'قواعد احتساب الضريبة', 'modal_title':'تعديل القاعدة', 'formset_title':'شرائح احتساب الضريبة'}
        if tax_rule.company_id.name == s.SPECIAL_COMPANY_NAME:
            messages.error(request, 'هذا البيان غير قابل للتعديل!!')
            return redirect('payroll:tax_rules_list', by='')
        elif request.method == 'POST':
            form = TaxRuleForm(request.POST, instance=tax_rule)
            formset = TaxSectionFormSet(request.POST, instance=tax_rule)
            for f in formset.forms:
                f.fields['DELETE'].label = 'حذف'
            if form.is_valid() and formset.is_valid():
                tax_rule = form.save()
                formset.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(tax_rule.name)
                messages.success(request, success_msg)
            else: # Form or/and formset were not valid
                # Spitting the errors coming from the form and formset
                [messages.error(request, error[0]) for error in form.errors.values()]
                for error_dict in formset.errors:
                    [messages.error(request, error[0]) for error in error_dict.values()]
        else: # request method is GET
            form = TaxRuleForm(instance=tax_rule)
            formset = TaxSectionFormSet(instance=tax_rule)
            for f in formset.forms:
                f.fields['DELETE'].label = 'حذف'
            modal_close_url = 'payroll:tax_rules_list'
            context['modal_close_url'] = modal_close_url
            context['editing'] = True
            try:
                tax_rules = TaxRule.objects.filter(Q(company_id=request.user.employee.company_id)|Q(company_id__name=s.SPECIAL_COMPANY_NAME))
                context['tax_rules'] = tax_rules
                context['form'] = form
                context['formset'] = formset
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'payroll/tax_rules_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('payroll:tax_rules_list', by='')