from django.conf.urls import url
from employees import views

app_name = 'employees'

urlpatterns = [
    url(r'^employees/(?P<by>[a-zA-Z_]*)$', views.employees_list, name='employees_list'),
    url(r'^import_export/', views.employee_upload, name='import_export'),
    url(r'^imp/employees/', views.employee_upload , name='import_button'),
    url(r'^exp/employees/', views.export_data , name='export_button'),
    url(r'^edit/employee/(?P<pk>\d+)/$', views.edit_employee, name='edit_employee'),
    url(r'^disable/employee/(?P<pk>\d+)/$', views.disable_employee, name='disable_employee'),
    url(r'^contracts/(?P<by>[a-zA-Z_]*)$', views.contracts_list, name='contracts_list'),
    url(r'^edit/contract/(?P<pk>\d+)/$', views.edit_contract, name='edit_contract'),
    url(r'^delete/contract/(?P<pk>\d+)/$', views.delete_contract, name='delete_contract'),
    url(r'^id_documents/(?P<by>[a-zA-Z_]*)$', views.id_documents_list, name='id_documents_list'),
    url(r'^edit/id_document/(?P<pk>\d+)/$', views.edit_id_document, name='edit_id_document'),
    url(r'^delete/id_document/(?P<pk>\d+)/$', views.delete_id_document, name='delete_id_document'),
    url(r'^education_degrees/(?P<by>[a-zA-Z_]*)$', views.education_degrees_list, name='education_degrees_list'),
    url(r'^edit/education_degree/(?P<pk>\d+)/$', views.edit_education_degree, name='edit_education_degree'),
    url(r'^delete/education_degree/(?P<pk>\d+)/$', views.delete_education_degree, name='delete_education_degree'),
    url(r'^genders/(?P<by>[a-zA-Z_]*)$', views.genders_list, name='genders_list'),
    url(r'^edit/gender/(?P<pk>\d+)/$', views.edit_gender, name='edit_gender'),
    url(r'^delete/gender/(?P<pk>\d+)/$', views.delete_gender, name='delete_gender'),
    url(r'^social_status/(?P<by>[a-zA-Z_]*)$', views.social_status_list, name='social_status_list'),
    url(r'^edit/social_status/(?P<pk>\d+)/$', views.edit_social_status, name='edit_social_status'),
    url(r'^delete/social_status/(?P<pk>\d+)/$', views.delete_social_status, name='delete_social_status'),
    url(r'^military_status/(?P<by>[a-zA-Z_]*)$', views.military_status_list, name='military_status_list'),
    url(r'^edit/military_status/(?P<pk>\d+)/$', views.edit_military_status, name='edit_military_status'),
    url(r'^delete/military_status/(?P<pk>\d+)/$', views.delete_military_status, name='delete_military_status'),
    url(r'^religions/(?P<by>[a-zA-Z_]*)$', views.religions_list, name='religions_list'),
    url(r'^edit/religion/(?P<pk>\d+)/$', views.edit_religion, name='edit_religion'),
    url(r'^delete/religion/(?P<pk>\d+)/$', views.delete_religion, name='delete_religion'),
]
