from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from home.forms import RequesterForm
from home.email_helper import Mailer
from companies.models import Company
from django.conf import settings as s
import os

def landing(request):
    if request.method == "POST":
        form = RequesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'تم ارسال طلبك بنجاح، سيتم التواصل معك فى أقرب وقت')

            # getting user data from the form
            user_email = form.clean()['email']
            user_name = form.clean()['name']

            # Sending a welcome email to the requester
            mailer = Mailer(s.ADMIN_EMAIL, s.ADMIN_EMAIL_PASS)
            template_path = os.path.join(s.BASE_DIR,'home','templates','home','emails','requester_welcome.html')
            with open(template_path, 'r') as f:
                msg_body = f.read().format(user_name)
            msg = mailer.create_msg(user_email,'Welcome to Moratabaty', msg_body)
            mailer.send_mail(msg)

            # Now sending a notification email to the Admin
            mailer = Mailer(s.ADMIN_EMAIL, s.ADMIN_EMAIL_PASS)
            template_path = os.path.join(s.BASE_DIR,'home','templates','home','emails','admin_notify.html')
            with open(template_path, 'r') as f:
                msg_body = f.read().format(user_name,user_email)
            msg = mailer.create_msg(s.ADMIN_EMAIL,'New User request', msg_body)
            mailer.send_mail(msg)
            
            # Cleaning the form from previous submitted data
            form = RequesterForm()
            context = {'form':form}
            return render(request, 'home/landing.html', context=context)
        else: 
            # Spitting the errors coming from the form
            [messages.error(request, error[0]) for error in form.errors.values()]
            # Cleaning the form from previous submitted data
            form = RequesterForm()
            context = {'form':form}
            return render(request, 'home/landing.html', context=context)
    else:
        # Request is GET type
        form = RequesterForm()
        context = {'form':form}
    return render(request, 'home/landing.html', context=context)

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home:dashboard'))
            else:
                messages.error(request, 'هذا الحساب موجود لدينا لكنه غير نشط!')
                return render(request, 'home/login.html')
        else:
            messages.error(request, 'لم تنجح عملية التسجيل، برجاء التحقق من البيانات المدخلة')
            return render(request, 'home/login.html')
    else:
        return render(request,'home/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:landing_page'))

@login_required
def dashboard(request):
    try:
        company = Company.objects.get(pk=request.user.employee.company_id.pk)
        context = {'company':company}
    except:
        context = {}
        messages.error(request, "لقد حدث خطأ ما، قد يكون هذا الحساب غير مسجل على شركة")
        return redirect('home:landing_page')
    return render(request,'home/homeboard.html', context=context)
