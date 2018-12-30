from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from attendance.models import Attendance, DayOffRule
from attendance.forms import AttendanceForm, DayOffRuleForm, DayOffFormSet
from django.http import HttpResponseForbidden

@login_required
def attendance_list(request, by):
    context = {'table_title':'بيانات الحضور', 'modal_title':'اضافة بيان حضور جديد', 'formset_title':'اجازات الموظف'}
    if request.method == "POST":
        form = AttendanceForm(request.user.employee.company_id, request.POST)
        formset = DayOffFormSet(request.POST)
        formset.can_delete = False
        formset_queryset = DayOffRule.objects.filter(company_id=request.user.employee.company_id)
        for f in formset.forms:
            f.fields['rule_id'].queryset=formset_queryset
        if form.is_valid():
            attendance = form.save(commit=False)
            formset = DayOffFormSet(request.POST, instance=attendance)
            formset.can_delete = False
            for f in formset.forms:
                f.fields['rule_id'].queryset=formset_queryset
            if formset.is_valid():
                attendance.save()
                formset.save()
                success_msg = 'تم اضافة "{}" بنجاح'.format(str(attendance))
                messages.success(request, success_msg)
                # Emptying the form and formset before rerendering them back
                form = AttendanceForm(request.user.employee.company_id)
                formset = DayOffFormSet()
                formset.can_delete = False
                for f in formset.forms:
                    f.fields['rule_id'].queryset=formset_queryset
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
            form = AttendanceForm(request.user.employee.company_id)
            formset = DayOffFormSet()
            formset.can_delete = False
            formset_queryset = DayOffRule.objects.filter(company_id=request.user.employee.company_id)
            for f in formset.forms:
                f.fields['rule_id'].queryset=formset_queryset
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'attendance/attendance_list.html', context=context)
    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
    if by != '':
        attendances = Attendance.objects.filter(employee_id__company_id=request.user.employee.company_id).order_by(by)
    else:
        attendances = Attendance.objects.filter(employee_id__company_id=request.user.employee.company_id)
    context['attendances'] = attendances
    context['form'] = form
    context['formset'] = formset
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'attendance/attendance_list.html', context=context)

@login_required
def delete_attendance(request, pk):
    try:
        attendance = Attendance.objects.get(pk=pk)
        if attendance.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if attendance.is_final:
            messages.error(request, 'هذا البيان نهائي و لا يمكن حذفة!')
            return redirect('attendance:attendance_list')
        attendance.delete()
        success_msg = 'تم حذف "{}" بنجاح'.format(str(attendance))
        messages.success(request, success_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('attendance:attendance_list', by='')

@login_required
def edit_attendance(request, pk):
    try:
        attendance = Attendance.objects.get(pk=pk)
        if attendance.employee_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if attendance.is_final:
            messages.error(request, 'هذا البيان نهائي و لا يمكن تعديلة!')
            return redirect('attendance:attendance_list')
        formset_queryset = DayOffRule.objects.filter(company_id=request.user.employee.company_id)
        context = {'table_title':'بيانات الحضور', 'modal_title':'تعديل بيان الحضور', 'formset_title':'اجازات الموظف'}
        if request.method == 'POST':
            form = AttendanceForm(request.user.employee.company_id, request.POST, instance=attendance)
            formset = DayOffFormSet(request.POST, instance=attendance)
            for f in formset.forms:
                f.fields['rule_id'].queryset=formset_queryset
                f.fields['DELETE'].label = 'حذف'
            if form.is_valid() and formset.is_valid():
                attendance = form.save()
                formset.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(str(attendance))
                messages.success(request, success_msg)
            else: # Form or/and formset were not valid
                # Spitting the errors coming from the form and formset
                [messages.error(request, error[0]) for error in form.errors.values()]
                for error_dict in formset.errors:
                    [messages.error(request, error[0]) for error in error_dict.values()]
        else: # request method is GET
            form = AttendanceForm(request.user.employee.company_id, instance=attendance)
            formset = DayOffFormSet(instance=attendance)
            for f in formset.forms:
                f.fields['rule_id'].queryset=formset_queryset
                f.fields['DELETE'].label = 'حذف'
            modal_close_url = 'attendance:attendance_list'
            context['modal_close_url'] = modal_close_url
            context['editing'] = True
            try:
                attendances = Attendance.objects.filter(employee_id__company_id=request.user.employee.company_id)
                context['attendances'] = attendances
                context['form'] = form
                context['formset'] = formset
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
            return render(request, 'attendance/attendance_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('attendance:attendance_list', by='')

@login_required
def day_off_rule_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = DayOffRuleForm(request.POST)
        if form.is_valid():
            day_off_rule = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(day_off_rule.name)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = DayOffRuleForm()
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'أنواع الاجازات', 'modal_title':'اضافة نوع اجازة جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = DayOffRuleForm()
        context = {'table_title':'أنواع الاجازات', 'modal_title':'اضافة نوع اجازة جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            day_off_rule_list = DayOffRule.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            day_off_rule_list = DayOffRule.objects.filter(company_id=request.user.employee.company_id)
        context['day_off_rule_list'] = day_off_rule_list
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'attendance/day_off_rule_list.html', context=context)

@login_required
def delete_day_off_rule(request, pk):
    try:
        day_off_rule = DayOffRule.objects.get(pk=pk)
        if day_off_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(day_off_rule.day_offs.all()) == 0:
            day_off_rule.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(day_off_rule.name)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(day_off_rule.name)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('attendance:attendance_settings', by='')

@login_required
def edit_day_off_rule(request, pk):
    try:
        day_off_rule = DayOffRule.objects.get(pk=pk)
        if day_off_rule.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = DayOffRuleForm(request.POST, instance=day_off_rule)
            if form.is_valid():
                day_off_rule = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(day_off_rule.name)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = DayOffRuleForm(instance=day_off_rule)
            modal_close_url = 'attendance:attendance_settings'
            context = {'table_title':'أنواع الاجازات', 'modal_title':'تعديل نوع الاجازة', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                day_off_rule_list = DayOffRule.objects.filter(company_id=request.user.employee.company_id)
                context['day_off_rule_list'] = day_off_rule_list
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'attendance/day_off_rule_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('attendance:attendance_settings', by='')
