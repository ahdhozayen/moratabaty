from django.conf.urls import url
from banks import views

app_name = 'banks'

urlpatterns = [
    url(r'^banks/(?P<by>[a-zA-Z_]*)$', views.banks_list, name='banks_list'),
    url(r'^delete/bank/(?P<pk>\d+)/$', views.delete_bank, name='delete_bank'),
    url(r'^edit/bank/(?P<pk>\d+)/$', views.edit_bank, name='edit_bank'),
    url(r'^accounts/(?P<by>[a-zA-Z_]*)$', views.accounts_list, name='accounts_list'),
    url(r'^delete/account/(?P<pk>\d+)/$', views.delete_account, name='delete_account'),
    url(r'^edit/account/(?P<pk>\d+)/$', views.edit_account, name='edit_account'),
]    