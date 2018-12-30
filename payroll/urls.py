from django.conf.urls import url
from payroll import views

app_name = 'payroll'

urlpatterns = [
    url(r'^salaries/(?P<by>[a-zA-Z_]*)$', views.salaries_list, name='salaries_list'),
    url(r'^delete/salary/(?P<pk>\d+)/$', views.delete_salary, name='delete_salary'),
    url(r'^edit/salary/(?P<pk>\d+)/$', views.edit_salary, name='edit_salary'),
    url(r'^finalize/salary/(?P<pk>\d+)/$', views.finalize_salary, name='finalize_salary'),
    url(r'^recalculate/salary/(?P<pk>\d+)/$', views.recalculate_salary, name='recalculate_salary'),
    url(r'^copy/salaries', views.copy_salaries, name='copy_salaries'),
    url(r'^send/payslips', views.send_payslips, name='send_payslips'),
    url(r'^salary_element_types/(?P<by>[a-zA-Z_]*)$', views.salary_element_types_list, name='salary_element_types_list'),
    url(r'^delete/salary_element_type/(?P<pk>\d+)/$', views.delete_salary_element_type, name='delete_salary_element_type'),
    url(r'^edit/salary_element_type/(?P<pk>\d+)/$', views.edit_salary_element_type, name='edit_salary_element_type'),
    url(r'^insurance_rules/(?P<by>[a-zA-Z_]*)$', views.insurance_rules_list, name='insurance_rules_list'),
    url(r'^delete/insurance_rule/(?P<pk>\d+)/$', views.delete_insurance_rule, name='delete_insurance_rule'),
    url(r'^edit/insurance_rule/(?P<pk>\d+)/$', views.edit_insurance_rule, name='edit_insurance_rule'),
    url(r'^custom_rules/(?P<by>[a-zA-Z_]*)$', views.custom_rules_list, name='custom_rules_list'),
    url(r'^delete/custom_rule/(?P<pk>\d+)/$', views.delete_custom_rule, name='delete_custom_rule'),
    url(r'^edit/custom_rule/(?P<pk>\d+)/$', views.edit_custom_rule, name='edit_custom_rule'),
    url(r'^tax_rules/(?P<by>[a-zA-Z_]*)$', views.tax_rules_list, name='tax_rules_list'),
    url(r'^delete/tax_rule/(?P<pk>\d+)/$', views.delete_tax_rule, name='delete_tax_rule'),
    url(r'^edit/tax_rule/(?P<pk>\d+)/$', views.edit_tax_rule, name='edit_tax_rule'),
]