from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from employees.models import (Employee, Contract, IdDocument,
                              EducationDegree, Gender, SocialStatus,
                              MilitaryStatus, Religion)
from employees.forms import (EmployeeForm, ContractForm, IdDocumentForm,
                             EducationDegreeForm, GenderForm, SocialStatusForm,
                             MilitaryStatusForm, ReligionForm)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseForbidden
from employees.resources import EmployeeResources
from django.http import HttpResponse
from tablib import Dataset
from django.utils.datastructures import MultiValueDictKeyError
import xlrd


@login_required
def employees_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = EmployeeForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            user_taken = None
            if 'picture' in request.FILES:
                employee.picture = request.FILES['picture']
            if employee.degree:
                employee.sub_section_id = employee.degree.sub_section_id
                employee.section_id = employee.degree.sub_section_id.section_id
                employee.department_id =  employee.degree.sub_section_id.section_id.department_id
                employee.branch_id = employee.degree.sub_section_id.section_id.department_id.branch_id
            if form.cleaned_data['user_name'] and form.cleaned_data['password']:
                username = form.cleaned_data['user_name']
                password = form.cleaned_data['password']
                first_name = employee.first_name
                last_name = employee.last_name
                user = User(username=username, password=password, first_name=first_name, last_name=last_name)
                try:
                    user.save()
                    employee.user_id = user.id
                except:
                    messages.error(request, "حساب المستخدم الذى تم ادخالة موجود من قبل، لم نتمكن من حفظ البيان!")
                    user_taken = True
                    form = EmployeeForm(request.user.employee.company_id, request.POST)
            if not user_taken:
                employee.save()
                success_msg = 'تم اضافة "{}" بنجاح'.format(employee.first_name)
                messages.success(request, success_msg)
                # Emptying the form before rerendering it back
                form = EmployeeForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الموظفين', 'modal_title':'اضافة موظف جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        try:
            # passing the company id to the form to filter on the current user company.
            form = EmployeeForm(request.user.employee.company_id)
            context = {'table_title':'الموظفين', 'modal_title':'اضافة موظف جديد', 'form':form}
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            employees = Employee.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            employees = Employee.objects.filter(company_id=request.user.employee.company_id)
        context['employees'] = employees
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        return render(request, 'employees/employees_list.html')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/employees_list.html', context=context)

# this function is used to export the employees data from db to excel file.
def export_data(request):
    employee_resources = EmployeeResources()
    dataset = employee_resources.export()
    # response = HttpResponse(dataset.csv, content_type='text/csv')
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')   # we can change the output file extention or type
    response['Content-Disposition'] = 'attachment; filename="employees.xls"'
    return response

# this function is used to import the employees data from excel file and insert them into db.
def employee_upload(request):
    # an empty list to fill later with the excel sheet header
    formHeader = list()
    # an empty list to fill later with the excel sheet rows
    formBody   = list()
    if request.method == 'POST':
        # calling the resource file we created to  get the employee from employee model.
        emp_resource = EmployeeResources()
        dataset = Dataset()
        if 'empFile' in request.FILES:      # file name comes from HTML page.
            new_employee = request.FILES['empFile']
            imported_data = dataset.load(new_employee.read())
            formHeader = imported_data.headers
            # start looping for the range of row count inside the excel sheet to get the rows
            for i in range(imported_data.height):
                formBody.append(imported_data[i])

            paginator = Paginator(formBody, 5) # Show 5 contacts per page
            page = request.GET.get('page')
            cases = paginator.get_page(page)
            # result = emp_resource.import_data(dataset, dry_run=True)  # Test the data import after importing
            # if not result.has_errors():
            #     emp_resource.import_data(dataset, dry_run=False)  # Actually import the data into db and save it.
        else:
            messages.error(request, 'No Such file, Or bad request.')
    myContext = {'formHeader':formHeader, 'formBody':formBody}
    return render(request, 'employees/employee_upload.html', myContext)

@login_required
def edit_employee(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
        if employee.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if employee.is_active == False: #user trying to access the edit page of the inactive employee from browser url
            messages.error(request, 'هذا البيان غير قابل للتعديل!!')
            return redirect('employees:employees_list', by='')
        if request.method == 'POST':
            form = EmployeeForm(request.user.employee.company_id, request.POST, instance=employee)
            if form.is_valid():
                if 'picture' in request.FILES:
                    image = request.FILES['picture']
                    extension = image.name.split('.')[-1]
                    if extension not in ['bmp', 'gif', 'png', 'ico', 'jpg', 'jpeg', 'psd']:
                        msg = "ملف الصورة يجب أن يكون واحد من هذة الأنواع فقط: 'bmp', 'gif', 'png', 'ico', 'jpg', 'jpeg', 'psd'"
                        messages.error(request, msg)
                        return redirect('employees:employees_list', by='')
                employee = form.save(commit=False)
                user_taken = None
                if 'picture' in request.FILES:
                    employee.picture = request.FILES['picture']
                if employee.degree:
                    employee.sub_section_id = employee.degree.sub_section_id
                    employee.section_id = employee.degree.sub_section_id.section_id
                    employee.department_id =  employee.degree.sub_section_id.section_id.department_id
                    employee.branch_id = employee.degree.sub_section_id.section_id.department_id.branch_id
                if form.cleaned_data['user_name'] and form.cleaned_data['password'] and not employee.user:
                    username = form.cleaned_data['user_name']
                    password = form.cleaned_data['password']
                    first_name = employee.first_name
                    last_name = employee.last_name
                    user = User(username=username, password=password, first_name=first_name, last_name=last_name)
                    try:
                        user.save()
                        employee.user_id = user.id
                    except:
                        messages.error(request, "حساب المستخدم الذى تم ادخالة موجود من قبل، لم نتمكن من حفظ البيان!")
                        user_taken = True
                        form = EmployeeForm(request.user.employee.company_id, request.POST)
                if not user_taken:
                    employee.save()
                    success_msg = 'تم تعديل "{}" بنجاح'.format(employee.first_name)
                    messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            if employee.user:
                initial = {'user_name':employee.user.username}
                form = EmployeeForm(request.user.employee.company_id, instance=employee, initial=initial)
                form.fields['user_name'].disabled = True
                form.fields['password'].disabled = True
            else:
                initial= {'user_name':''}
                form = EmployeeForm(request.user.employee.company_id, instance=employee, initial=initial)
            modal_close_url = 'employees:employees_list'
            context = {'table_title':'الموظفين', 'modal_title':'تعديل بيانات الموظف', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                employees = Employee.objects.filter(company_id=request.user.employee.company_id)
                context['employees'] = employees
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/employees_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:employees_list', by='')

@login_required
def disable_employee(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
        if employee.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if employee.user:
            user = employee.user
            user.is_active = False
            user.save()
        employee.is_active = False
        employee.save()
        success_msg = 'تم ايقاف "{}" بنجاح'.format(employee.first_name)
        messages.success(request, success_msg)
    except:
        error_msg = 'لم يتم الايقاف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:employees_list', by='')

@login_required
def contracts_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(contract.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = ContractForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'أنواع التعاقد (العقود)', 'modal_title':'اضافة عقد جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = ContractForm()
        context = {'table_title':'أنواع التعاقد (العقود)', 'modal_title':'اضافة عقد جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            contracts = Contract.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            contracts = Contract.objects.filter(company_id=request.user.employee.company_id)
        context['contracts'] = contracts
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/contracts_list.html', context=context)

@login_required
def edit_contract(request, pk):
    try:
        contract = Contract.objects.get(pk=pk)
        if contract.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = ContractForm(request.POST, instance=contract)
            if form.is_valid():
                contract = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(contract.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = ContractForm(instance=contract)
            modal_close_url = 'employees:contracts_list'
            context = {'table_title':'أنواع التعاقد (العقود)', 'modal_title':'تعديل العقد', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                contracts = Contract.objects.filter(company_id=request.user.employee.company_id)
                context['contracts'] = contracts
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/contracts_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:contracts_list', by='')

@login_required
def delete_contract(request, pk):
    try:
        contract = Contract.objects.get(pk=pk)
        if contract.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(contract.employees.all()) == 0:
            contract.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(contract.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(contract.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:contracts_list', by='')

@login_required
def id_documents_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = IdDocumentForm(request.POST)
        if form.is_valid():
            id_document = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(id_document.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = IdDocumentForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'أنواع وثائق الهوية', 'modal_title':'اضافة نوع وثيقة جديدة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = IdDocumentForm()
        context = {'table_title':'أنواع وثائق الهوية', 'modal_title':'اضافة نوع وثيقة جديدة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            id_documents = IdDocument.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            id_documents = IdDocument.objects.filter(company_id=request.user.employee.company_id)
        context['id_documents'] = id_documents
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/id_documents_list.html', context=context)

@login_required
def edit_id_document(request, pk):
    try:
        id_document = IdDocument.objects.get(pk=pk)
        if id_document.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = IdDocumentForm(request.POST, instance=id_document)
            if form.is_valid():
                id_document = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(id_document.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = IdDocumentForm(instance=id_document)
            modal_close_url = 'employees:id_documents_list'
            context = {'table_title':'أنواع وثائق الهوية', 'modal_title':'تعديل وثيقة الهوية', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                id_documents = IdDocument.objects.filter(company_id=request.user.employee.company_id)
                context['id_documents'] = id_documents
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/id_documents_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:id_documents_list', by='')

@login_required
def delete_id_document(request, pk):
    try:
        id_document = IdDocument.objects.get(pk=pk)
        if id_document.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(id_document.employees.all()) == 0:
            id_document.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(id_document.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(id_document.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:id_documents_list', by='')

@login_required
def education_degrees_list(request, by=''):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = EducationDegreeForm(request.POST)
        if form.is_valid():
            education_degree = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(education_degree.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = EducationDegreeForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الدرجات التعليمية', 'modal_title':'اضافة درجة تعليمية جديدة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = EducationDegreeForm()
        context = {'table_title':'الدرجات التعليمية', 'modal_title':'اضافة درجة تعليمية جديدة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            education_degrees = EducationDegree.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            education_degrees = EducationDegree.objects.filter(company_id=request.user.employee.company_id)
        context['education_degrees'] = education_degrees
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/education_degrees_list.html', context=context)

@login_required
def edit_education_degree(request, pk):
    try:
        education_degree = EducationDegree.objects.get(pk=pk)
        if education_degree.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = EducationDegreeForm(request.POST, instance=education_degree)
            if form.is_valid():
                education_degree = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(education_degree.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = EducationDegreeForm(instance=education_degree)
            modal_close_url = 'employees:education_degrees_list'
            context = {'table_title':'الدرجات التعليمية', 'modal_title':'تعديل الدرجة التعليمية', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                education_degrees = EducationDegree.objects.filter(company_id=request.user.employee.company_id)
                context['education_degrees'] = education_degrees
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/education_degrees_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:education_degrees_list', by='')

@login_required
def delete_education_degree(request, pk):
    try:
        education_degree = EducationDegree.objects.get(pk=pk)
        if education_degree.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(education_degree.employees.all()) == 0:
            education_degree.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(education_degree.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(education_degree.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:education_degrees_list', by='')

@login_required
def genders_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = GenderForm(request.POST)
        if form.is_valid():
            gender = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(gender.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = GenderForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'نوع (جنس) الموظف', 'modal_title':'اضافة نوع جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = GenderForm()
        context = {'table_title':'نوع (جنس) الموظف', 'modal_title':'اضافة نوع جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            genders = Gender.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            genders = Gender.objects.filter(company_id=request.user.employee.company_id)
        context['genders'] = genders
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/genders_list.html', context=context)

@login_required
def edit_gender(request, pk):
    try:
        gender = Gender.objects.get(pk=pk)
        if gender.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = GenderForm(request.POST, instance=gender)
            if form.is_valid():
                gender = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(gender.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = GenderForm(instance=gender)
            modal_close_url = 'employees:genders_list'
            context = {'table_title':'نوع (جنس) الموظف', 'modal_title':'تعديل النوع', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                genders = Gender.objects.filter(company_id=request.user.employee.company_id)
                context['genders'] = genders
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/genders_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:genders_list', by='')

@login_required
def delete_gender(request, pk):
    try:
        gender = Gender.objects.get(pk=pk)
        if gender.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(gender.employees.all()) == 0:
            gender.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(gender.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(gender.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:genders_list', by='')

@login_required
def social_status_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = SocialStatusForm(request.POST)
        if form.is_valid():
            social_status = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(social_status.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = SocialStatusForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الحالات الاجتماعية', 'modal_title':'اضافة حالة اجتماعية جديدة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = SocialStatusForm()
        context = {'table_title':'الحالات الاجتماعية', 'modal_title':'اضافة حالة اجتماعية جديدة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            social_status_list = SocialStatus.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            social_status_list = SocialStatus.objects.filter(company_id=request.user.employee.company_id)
        context['social_status_list'] = social_status_list
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/social_status_list.html', context=context)

@login_required
def edit_social_status(request, pk):
    try:
        social_status = SocialStatus.objects.get(pk=pk)
        if social_status.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = SocialStatusForm(request.POST, instance=social_status)
            if form.is_valid():
                social_status = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(social_status.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = SocialStatusForm(instance=social_status)
            modal_close_url = 'employees:social_status_list'
            context = {'table_title':'الحالات الاجتماعية', 'modal_title':'تعديل الحالة الاجتماعية', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                social_status_list = SocialStatus.objects.filter(company_id=request.user.employee.company_id)
                context['social_status_list'] = social_status_list
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/social_status_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:social_status_list', by='')

@login_required
def delete_social_status(request, pk):
    try:
        social_status = SocialStatus.objects.get(pk=pk)
        if social_status.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(social_status.employees.all()) == 0:
            social_status.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(social_status.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(social_status.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:social_status_list', by='')

@login_required
def military_status_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = MilitaryStatusForm(request.POST)
        if form.is_valid():
            military_status = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(military_status.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = MilitaryStatusForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الموقف من التجنيد', 'modal_title':'اضافة موقف تجنيدي جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = MilitaryStatusForm()
        context = {'table_title':'الموقف من التجنيد', 'modal_title':'اضافة موقف تجنيدي جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            military_status_list = MilitaryStatus.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            military_status_list = MilitaryStatus.objects.filter(company_id=request.user.employee.company_id)
        context['military_status_list'] = military_status_list
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/military_status_list.html', context=context)

@login_required
def edit_military_status(request, pk):
    try:
        military_status = MilitaryStatus.objects.get(pk=pk)
        if military_status.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = MilitaryStatusForm(request.POST, instance=military_status)
            if form.is_valid():
                military_status = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(military_status.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = MilitaryStatusForm(instance=military_status)
            modal_close_url = 'employees:military_status_list'
            context = {'table_title':'الموقف من التجنيد', 'modal_title':'تعديل الموقف التجنيدي', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                military_status_list = MilitaryStatus.objects.filter(company_id=request.user.employee.company_id)
                context['military_status_list'] = military_status_list
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/military_status_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:military_status_list', by='')

@login_required
def delete_military_status(request, pk):
    try:
        military_status = MilitaryStatus.objects.get(pk=pk)
        if military_status.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(military_status.employees.all()) == 0:
            military_status.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(military_status.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(military_status.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:military_status_list', by='')

@login_required
def religions_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = ReligionForm(request.POST)
        if form.is_valid():
            religion = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(religion.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = ReligionForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الديانات', 'modal_title':'اضافة ديانة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = ReligionForm()
        context = {'table_title':'الديانات', 'modal_title':'اضافة ديانة', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            religions = Religion.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            religions = Religion.objects.filter(company_id=request.user.employee.company_id)
        context['religions'] = religions
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'employees/religions_list.html', context=context)

@login_required
def edit_religion(request, pk):
    try:
        religion = Religion.objects.get(pk=pk)
        if religion.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = ReligionForm(request.POST, instance=religion)
            if form.is_valid():
                religion = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(religion.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = ReligionForm(instance=religion)
            modal_close_url = 'employees:religions_list'
            context = {'table_title':'الديانات', 'modal_title':'تعديل اسم الديانة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                religions = Religion.objects.filter(company_id=request.user.employee.company_id)
                context['religions'] = religions
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'employees/religions_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'
        messages.error(request, error_msg)
    return redirect('employees:religions_list', by='')

@login_required
def delete_religion(request, pk):
    try:
        religion = Religion.objects.get(pk=pk)
        if religion.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(religion.employees.all()) == 0:
            religion.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(religion.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(religion.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('employees:religions_list', by='')
