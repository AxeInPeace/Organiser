from django.conf.urls import url
from . import views

__schedule_add_urls = [
    url(r'^add_task$', views.add_task, name='add_task'),
    url(r'^add_event$', views.add_event, name='add_event'),
    url(r'^add_schedule$', views.add_schedule, name='add_schedule'),
    url(r'^add_place$', views.add_place, name='add_place'),
]

__schedule_change_urls = [
    url(r'^change_events$', views.change_events, name='change_events'),
    url(r'^change_tasks$', views.change_tasks, name='change_tasks'),
    url(r'^change_places$', views.change_places, name='change_places'),
    url(r'^change_schedules$', views.change_schedules, name='change_schedules'),

]

__schedule_delete_urls = [
    url(r'^delete_event$', views.delete_event, name='delete_event'),
    url(r'^delete_task$', views.delete_task, name='delete_task'),
    url(r'^delete_place$', views.delete_places, name='delete_place'),
    url(r'^delete_schedule$', views.delete_schedule, name='delete_schedule'),
]

schedule_urls = __schedule_add_urls + __schedule_change_urls + __schedule_delete_urls + [
    url(r'^$', views.main, name='main'),
    url(r'^generate_schedule$', views.generate_shedule, name='generate_schedule'),
    url('^search_schedule$', views.render_table_schedule, name='change_schedule_table'),
    url(r'^change_task_status$', views.change_task_status, name='change_task_status'),
    url(r'^time_places$', views.time_for_places, name='time_places'),
]
