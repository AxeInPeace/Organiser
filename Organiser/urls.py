from django.conf.urls import url, include
from django.contrib import admin
from .registration.urls import regurls
from .schedule.urls import shedurls

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include(regurls)),
    url(r'^', include(shedurls)),
]
