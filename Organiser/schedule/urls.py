from django.conf.urls import url
from . import views

schedule_urls = [
    url(r'^$', views.main, name='main'),
    url(r'^add_task$', views.add_task, name='add_task'),
    url(r'^add_event$', views.add_event, name='add_event'),
    url(r'^add_schedule$', views.add_schedule, name='add_schedule'),
    url(r'^add_place$', views.add_place, name='add_place'),
    url(r'^generate_schedule$', views.generate_shedule, name='generate_schedule'),
]
