from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Schedule)
admin.site.register(EventRepetition)
admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Place)
admin.site.register(Distance)
