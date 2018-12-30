from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from companies.models import Company, Branch, Department, Section, SubSection, Degree
from companies.forms import CompanyForm, BranchForm, DepartmentForm, SectionForm, SubSectionForm, DegreeForm
from django.http import HttpResponseForbidden
@login_required
def branches_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(branch.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = BranchForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'أفرع الشركة', 'modal_title':'اضافة فرع جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = BranchForm()
        context = {'table_title':'أفرع الشركة', 'modal_title':'اضافة فرع جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            branches = Branch.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            branches = Branch.objects.filter(company_id=request.user.employee.company_id)
        context['branches'] = branches
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'companies/branches_list.html', context=context)

@login_required
def delete_branch(request, pk):
    try:
        branch = Branch.objects.get(pk=pk)
        if branch.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(branch.departments.all()) == 0 and len(branch.employees.all()) == 0:
            branch.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(branch.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(branch.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('companies:branches_list', by='')

@login_required
def edit_branch(request, pk):
    try:
        branch = Branch.objects.get(pk=pk)
        if branch.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = BranchForm(request.POST, instance=branch)
            if form.is_valid():
                branch = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(branch.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = BranchForm(instance=branch)
            modal_close_url = 'companies:branches_list'
            context = {'table_title':'أفرع الشركة', 'modal_title':'تعديل بيانات الفرع', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                branches = Branch.objects.filter(company_id=request.user.employee.company_id)
                context['branches'] = branches
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'companies/branches_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('companies:branches_list', by='')

@login_required
def departments_list(request, by):
    if request.method == "POST":
        form = DepartmentForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            department = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(department.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = DepartmentForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الادارات', 'modal_title':'اضافة ادارة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        context = {'table_title':'الادارات', 'modal_title':'اضافة ادارة'}
        try:
            # Just passing an empty form to be rendered in case of GET
            form = DepartmentForm(request.user.employee.company_id)
            context['form'] = form
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            departments = Department.objects.filter(branch_id__company_id=request.user.employee.company_id).order_by(by)
        else:
            departments = Department.objects.filter(branch_id__company_id=request.user.employee.company_id)
        context['departments'] = departments
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'companies/departments_list.html', context=context)

@login_required
def delete_department(request, pk):
    try:
        department = Department.objects.get(pk=pk)
        if department.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(department.employees.all()) == 0:
            department.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(department.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(department.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('companies:departments_list', by='')

@login_required
def edit_department(request, pk):
    try:
        department = Department.objects.get(pk=pk)
        if department.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = DepartmentForm(request.user.employee.company_id, request.POST, instance=department)
            if form.is_valid():
                department = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(department.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = DepartmentForm(request.user.employee.company_id ,instance=department)
            modal_close_url = 'companies:departments_list'
            context = {'table_title':'الادارات', 'modal_title':'تعديل بيانات الادارة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                departments = Department.objects.filter(branch_id__company_id=request.user.employee.company_id)
                context['departments'] = departments
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'companies/departments_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('companies:departments_list', by='')

@login_required
def sections_list(request, by):
    if request.method == "POST":
        form = SectionForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            section = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(section.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = SectionForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الاقسام', 'modal_title':'اضافة قسم', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        context = {'table_title':'الاقسام', 'modal_title':'اضافة قسم'}
        try:
            # Just passing an empty form to be rendered in case of GET
            form = SectionForm(request.user.employee.company_id)
            context['form'] = form
        except:
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            sections = Section.objects.filter(department_id__branch_id__company_id=request.user.employee.company_id).order_by(by)
        else:
            sections = Section.objects.filter(department_id__branch_id__company_id=request.user.employee.company_id)
        context['sections'] = sections
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'companies/sections_list.html', context=context)

@login_required
def delete_section(request, pk):
    try:
        section = Section.objects.get(pk=pk)
        if section.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(section.employees.all()) == 0:
            section.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(section.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(section.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('companies:sections_list', by='')

@login_required
def edit_section(request, pk):
    try:
        section = Section.objects.get(pk=pk)
        if section.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = SectionForm(request.user.employee.company_id, request.POST, instance=section)
            if form.is_valid():
                section = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(section.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = SectionForm(request.user.employee.company_id ,instance=section)
            modal_close_url = 'companies:sections_list'
            context = {'table_title':'الاقسام', 'modal_title':'تعديل بيانات القسم', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                sections = Section.objects.filter(department_id__branch_id__company_id=request.user.employee.company_id)
                context['sections'] = sections
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'companies/sections_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('companies:sections_list', by='')

@login_required
def sub_sections_list(request, by):
    if request.method == "POST":
        form = SubSectionForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            sub_section = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(sub_section.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = SubSectionForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الوظائف', 'modal_title':'اضافة وظيفة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        context = {'table_title':'الوظائف', 'modal_title':'اضافة وظيفة'}
        try:
            # Just passing an empty form to be rendered in case of GET
            form = SubSectionForm(request.user.employee.company_id)
            context['form'] = form
        except:
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            sub_sections = SubSection.objects.filter(section_id__department_id__branch_id__company_id=request.user.employee.company_id).order_by(by)
        else:
            sub_sections = SubSection.objects.filter(section_id__department_id__branch_id__company_id=request.user.employee.company_id)
        context['sub_sections'] = sub_sections
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'companies/sub_sections_list.html', context=context)

@login_required
def delete_sub_section(request, pk):
    try:
        sub_section = SubSection.objects.get(pk=pk)
        if sub_section.section_id.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(sub_section.employees.all()) == 0 and len(sub_section.degrees.all()) == 0:
            sub_section.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(sub_section.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(sub_section.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('companies:sub_sections_list', by='')

@login_required
def edit_sub_section(request, pk):
    try:
        sub_section = SubSection.objects.get(pk=pk)
        if sub_section.section_id.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = SubSectionForm(request.user.employee.company_id, request.POST, instance=sub_section)
            if form.is_valid():
                sub_section = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(sub_section.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = SubSectionForm(request.user.employee.company_id ,instance=sub_section)
            modal_close_url = 'companies:sub_sections_list'
            context = {'table_title':'الوظائف', 'modal_title':'تعديل بيانات الوظيفة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                sub_sections = SubSection.objects.filter(section_id__department_id__branch_id__company_id=request.user.employee.company_id)
                context['sub_sections'] = sub_sections
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'companies/sub_sections_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('companies:sub_sections_list', by='')

@login_required
def degrees_list(request, by):
    if request.method == "POST":
        form = DegreeForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            degree = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(degree.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = SubSectionForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'الدرجات', 'modal_title':'اضافة درجة', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        context = {'table_title':'الدرجات', 'modal_title':'اضافة درجة'}
        try:
            # Just passing an empty form to be rendered in case of GET
            form = DegreeForm(request.user.employee.company_id)
            context['form'] = form
        except:
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            degrees = Degree.objects.filter(sub_section_id__section_id__department_id__branch_id__company_id=request.user.employee.company_id).order_by(by)
        else:
            degrees = Degree.objects.filter(sub_section_id__section_id__department_id__branch_id__company_id=request.user.employee.company_id)
        context['degrees'] = degrees
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'companies/degrees_list.html', context=context)

@login_required
def delete_degree(request, pk):
    try:
        degree = Degree.objects.get(pk=pk)
        if degree.sub_section_id.section_id.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(degree.employees.all()) == 0 :
            degree.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(degree.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(degree.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('companies:degrees_list', by='')

@login_required
def edit_degree(request, pk):
    try:
        degree = Degree.objects.get(pk=pk)
        if degree.sub_section_id.section_id.department_id.branch_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = DegreeForm(request.user.employee.company_id, request.POST, instance=degree)
            if form.is_valid():
                degree = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(degree.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = DegreeForm(request.user.employee.company_id ,instance=degree)
            modal_close_url = 'companies:degrees_list'
            context = {'table_title':'الدرجات', 'modal_title':'تعديل بيانات الدرجة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                degrees = Degree.objects.filter(sub_section_id__section_id__department_id__branch_id__company_id=request.user.employee.company_id)
                context['degrees'] = degrees
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'companies/degrees_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('companies:degrees_list', by='')

@login_required
def settings(request):
    try:
        company = Company.objects.get(pk=request.user.employee.company_id.pk)
        if request.method == 'POST':
            form = CompanyForm(request.POST, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم تغيير اسم الشركة بنجاح')
                form = CompanyForm(instance=company)
                context = {'company':company, 'form': form}
                return render(request, 'companies/settings.html', context=context)
            else:
                [messages.error(request, error[0]) for error in form.errors.values()]
                return redirect('companies:settings')
        else:
            form = CompanyForm(instance=company)
            context = {'company':company, 'form': form}
            return render(request, 'companies/settings.html', context=context)
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        return render(request, 'companies/settings.html', context=context)