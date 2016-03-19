from django.conf.urls import url
from . import views

regurls = [
    url(r'^signup$', views.registration, name='signup'),
    url(r'^signin$', views.signin, name='signin'),
    url(r'^signout$', views.signout, name='signout'),
    url(r'^ajax_mail$', views.ajax_email, name='ajax_mail'),
    url(r'^ajax_pass$', views.ajax_pass, name='ajax_pass'),
    url(r'^ajax_check_pass$', views.ajax_check_pass, name='ajax_check_pass'),
]