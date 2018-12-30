from django.conf.urls import url
from companies import views

app_name = 'companies'

urlpatterns = [
    url(r'^branches/(?P<by>[a-zA-Z_]*)$', views.branches_list, name='branches_list'),
    url(r'^delete/branch/(?P<pk>\d+)/$', views.delete_branch, name='delete_branch'),
    url(r'^edit/branch/(?P<pk>\d+)/$', views.edit_branch, name='edit_branch'),
    url(r'^departments/(?P<by>[a-zA-Z_]*)$', views.departments_list, name='departments_list'),
    url(r'^delete/department/(?P<pk>\d+)/$', views.delete_department, name='delete_department'),
    url(r'^edit/department/(?P<pk>\d+)/$', views.edit_department, name='edit_department'),
    url(r'^sections/(?P<by>[a-zA-Z_]*)$', views.sections_list, name='sections_list'),
    url(r'^delete/section/(?P<pk>\d+)/$', views.delete_section, name='delete_section'),
    url(r'^edit/section/(?P<pk>\d+)/$', views.edit_section, name='edit_section'),
    url(r'^sub_sections/(?P<by>[a-zA-Z_]*)$', views.sub_sections_list, name='sub_sections_list'),
    url(r'^delete/sub_section/(?P<pk>\d+)/$', views.delete_sub_section, name='delete_sub_section'),
    url(r'^edit/sub_section/(?P<pk>\d+)/$', views.edit_sub_section, name='edit_sub_section'),
    url(r'^degrees/(?P<by>[a-zA-Z_]*)$', views.degrees_list, name='degrees_list'),
    url(r'^delete/degree/(?P<pk>\d+)/$', views.delete_degree, name='delete_degree'),
    url(r'^edit/degree/(?P<pk>\d+)/$', views.edit_degree, name='edit_degree'),
    url(r'^settings/', views.settings, name='settings'),
]    

