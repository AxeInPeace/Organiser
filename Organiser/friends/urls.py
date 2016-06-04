from django.conf.urls import url

from . import views

friends_urls = [
    url(r'^$', views.my_friends, name='my_friends'),
    url(r'^(?P<id>([0-9]+))$', views.friend, name='friend'),
    url(r'^search_friends$', views.search_friends, name='search_friends'),
    url(r'^send(?P<id>([0-9]+))$', views.send_request, name='send_request'),
    url(r'^accept(?P<id>([0-9]+))$', views.accept_request, name='accept_request'),
    url(r'^decline(?P<id>([0-9]+))$', views.decline_request, name='decline_request'),
]

import_export_urls = [
    url(r'^import_schedule$', views.import_schedule, name='import_schedule'),
    url(r'^export_schedule$', views.export_schedule, name='export_schedule'),
]
