from django.conf.urls import url
from attendance import views

app_name = 'attendance'

urlpatterns = [
    url(r'^attendances/(?P<by>[a-zA-Z_]*)$', views.attendance_list, name='attendance_list'),
    url(r'^delete/attendance/(?P<pk>\d+)/$', views.delete_attendance, name='delete_attendance'),
    url(r'^edit/attendance/(?P<pk>\d+)/$', views.edit_attendance, name='edit_attendance'),
    url(r'^settings/(?P<by>[a-zA-Z_]*)$', views.day_off_rule_list, name='attendance_settings'),
    url(r'^delete/dayoffrule/(?P<pk>\d+)/$', views.delete_day_off_rule, name='delete_day_off_rule'),
    url(r'^edit/dayoffrule/(?P<pk>\d+)/$', views.edit_day_off_rule, name='edit_day_off_rule'),
]