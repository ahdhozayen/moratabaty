"""mashreq_hr_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from mashreq_hr_project import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/', include('home.urls'), name="home"),
    url(r'^$', views.redirect, name='redirect'),
    url(r'^company/', include('companies.urls'), name='companies'),
    url(r'^employees/', include('employees.urls'), name='employees'),
    url(r'attendance/', include('attendance.urls'), name='attendance'),
    url(r'payroll/', include('payroll.urls'), name='payroll'),
    url(r'banks/', include('banks.urls'), name='banks'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site global customizations
admin.site.site_header = 'Mashreq Arabia - HR'
admin.site.site_title = 'Mashreq Arabia - HR'