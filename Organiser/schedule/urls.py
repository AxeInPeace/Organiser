from django.conf.urls import url
from . import views

shedurls = [
    url(r'^$', views.main, name='main'),

]