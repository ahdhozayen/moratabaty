from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from banks.models import Bank, BankAccount
from banks.forms import BankForm, BankAccountForm
from django.http import HttpResponseForbidden

@login_required
def banks_list(request, by):
    if request.method == "POST":
        # Adding the company_id from the user model
        request.POST = request.POST.copy()  #converting the QueryDict to a mutable one
        request.POST['company_id'] = request.user.employee.company_id.pk
        form = BankForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            bank = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(bank.name +' - '+ bank.branch)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = BankForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'البنوك', 'modal_title':'اضافة بنك جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        # Just passing an empty form to be rendered in case of GET
        form = BankForm(request.user.employee.company_id)
        context = {'table_title':'البنوك', 'modal_title':'اضافة بنك جديد', 'form':form}
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            banks = Bank.objects.filter(company_id=request.user.employee.company_id).order_by(by)
        else:
            banks = Bank.objects.filter(company_id=request.user.employee.company_id)
        context['banks'] = banks
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        context.pop('form')
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'banks/banks_list.html', context=context)

@login_required
def delete_bank(request, pk):
    try:
        bank = Bank.objects.get(pk=pk)
        if bank.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(bank.accounts.all()) == 0:
            bank.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(bank.name +' - '+ bank.branch)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(bank.name +' - '+ bank.branch)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('banks:banks_list', by='')

@login_required
def edit_bank(request, pk):
    try:
        bank = Bank.objects.get(pk=pk)
        if bank.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            form = BankForm(request.user.employee.company_id, request.POST, instance=bank)
            if form.is_valid():
                bank = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(bank.name +' - '+ bank.branch)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = BankForm(request.user.employee.company_id, instance=bank)
            modal_close_url = 'banks:banks_list'
            context = {'table_title':'البنوك', 'modal_title':'تعديل بيانات البنك', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                banks = Bank.objects.filter(company_id=request.user.employee.company_id)
                context['banks'] = banks
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'banks/banks_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('banks:banks_list', by='')

@login_required
def accounts_list(request, by):
    if request.method == "POST":
        if request.POST['account_type'] == 'company':
            request.POST = request.POST.copy()
            request.POST['account_company_holder'] = request.user.employee.company_id.pk
        form = BankAccountForm(request.user.employee.company_id, request.POST)
        if form.is_valid():
            bank_account = form.save()
            success_msg = 'تم اضافة "{}" بنجاح'.format(bank_account.account_number+'/'+bank_account.bank_id.name+'-'+bank_account.bank_id.branch)
            messages.success(request, success_msg)
            # Emptying the form before rerendering it back
            form = BankAccountForm(request.user.employee.company_id)
        else: # Form was not valid
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
        # Handling the "save and add another" button
        if 'save_and_add' in request.POST:
            save_and_add = True
        else:
            save_and_add = False
        context = {'table_title':'حسابات البنوك', 'modal_title':'اضافة حساب جديد', 'save_and_add':save_and_add, 'form':form}
    else:   # Request is GET
        context = {'table_title':'حسابات البنوك', 'modal_title':'اضافة حساب جديد'}
        try:
            # Just passing an empty form to be rendered in case of GET
            form = BankAccountForm(request.user.employee.company_id)
            context['form'] = form
        except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
            messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    try:    # Either GET or POST, We will render a table containing objects with company_id equals to user's company_id
        if by != '':
            bank_accounts = BankAccount.objects.filter(bank_id__company_id=request.user.employee.company_id).order_by(by)
        else:
            bank_accounts = BankAccount.objects.filter(bank_id__company_id=request.user.employee.company_id)
        context['bank_accounts'] = bank_accounts
    except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
    # Finally, and In all the cases, we will always render the same page to the user
    return render(request, 'banks/accounts_list.html', context=context)

def delete_account(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
        if bank_account.bank_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if len(bank_account.transfer_to_bank.all()) == 0:
            bank_account.delete()
            success_msg = 'تم حذف "{}" بنجاح'.format(bank_account.account_number+'/'+bank_account.bank_id.name+'-'+bank_account.bank_id.branch)
            messages.success(request, success_msg)
        else:
            error_msg = 'لا يمكن حذف "{}" لوجود بيانات أخرى مسجلة علية'.format(bank_account.account_number+'/'+bank_account.bank_id.name+'-'+bank_account.bank_id.branch)
            messages.error(request, error_msg)
    except:
        error_msg = 'لم يتم الحذف المطلوب، خطأ ما قد حدث'
        messages.error(request, error_msg)
    return redirect('banks:accounts_list', by='')

def edit_account(request, pk):
    try:
        bank_account = BankAccount.objects.get(pk=pk)
        if bank_account.bank_id.company_id != request.user.employee.company_id:
            return HttpResponseForbidden("<h1>Access Denied! </h1>")
        if request.method == 'POST':
            request.POST = request.POST.copy()
            if request.POST['account_type'] == 'company':
                request.POST['account_company_holder'] = request.user.employee.company_id.pk
            elif request.POST['account_type'] == 'employee':
                request.POST.pop('account_company_holder')
            form = BankAccountForm(request.user.employee.company_id, request.POST, instance=bank_account)
            if form.is_valid():
                bank_account = form.save()
                success_msg = 'تم تعديل "{}" بنجاح'.format(bank_account.account_number+'/'+bank_account.bank_id.name+'-'+bank_account.bank_id.branch)
                messages.success(request, success_msg)
            else: # Form was not valid
                # Spitting the errors coming from the form
                [messages.error(request, error[0]) for error in form.errors.values()]
        else: # request method is GET
            form = BankAccountForm(request.user.employee.company_id, instance=bank_account)
            modal_close_url = 'banks:accounts_list'
            context = {'table_title':'حسابات البنوك', 'modal_title':'تعديل بيانات الحساب', 'editing':True, 'modal_close_url':modal_close_url, 'form':form}
            try:
                bank_accounts = BankAccount.objects.filter(bank_id__company_id=request.user.employee.company_id)
                context['bank_accounts'] = bank_accounts
            except: # Just in case the logged user is not tied to an employee account (i.e. doesn't have a company_id)
                messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
                context.pop('form')
            return render(request, 'banks/accounts_list.html', context=context)
    except:
        error_msg = 'لم يتم العثور على البيان المطلوب، قد يكون قد تم حذفة من قبل'     
        messages.error(request, error_msg)
    return redirect('banks:accounts_list', by='')