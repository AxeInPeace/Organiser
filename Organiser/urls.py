from django.conf.urls import url, include
from django.contrib import admin
from .registration.urls import regurls
from .schedule.urls import schedule_urls

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include(regurls)),
    url(r'^', include(schedule_urls)),
]
