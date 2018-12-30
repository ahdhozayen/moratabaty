from django.conf.urls import url
from home import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.landing, name='landing_page'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^login/', views.user_login, name='login'),
    url(r'^logout/', views.user_logout, name='logout'),
    
]