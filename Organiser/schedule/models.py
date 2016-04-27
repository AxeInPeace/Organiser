from django.db import models
from django.contrib.auth.models import User


class Place(models.Model):
    name = models.CharField(max_length=1000)
    user = models.ForeignKey(User)


class Schedule(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=1000)
    priority = models.IntegerField()


class Event(models.Model):
    def __str__(self):
        return self.name + ' ' + str(self.start_time) + ' ' + str(self.end_time)
    name = models.CharField(max_length=1000)
    schedule = models.ForeignKey(Schedule)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    place = models.ForeignKey(Place)


class EventRepetition(models.Model):
    def __str__(self):
        return self.event.name + str(self.start_day)
    event = models.ForeignKey(Event)
    start_day = models.DateField()
    repetition = models.DurationField() #repeat every repetition time
    amount = models.IntegerField()      #how many times Task will repeat


class Task(models.Model):
    def __str__(self):
        return self.name + ' ' + str(self.start_time) + ' ' + str(self.end_time)
    name = models.CharField(max_length=1000)
    user = models.ForeignKey(User)
    longitude = models.DurationField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    deadline = models.DateTimeField()


class TaskHierarchy(models.Model):
    ancestor = models.ForeignKey(Task, related_name='ancestor')
    me = models.ForeignKey(Task, related_name='child')


class TaskRepetition(models.Model):
    task = models.ForeignKey(Task)
    repetition = models.DurationField() #repeat every repetition time
    amount = models.IntegerField()      #how many times Task will repeat


class PlacesForTask(models.Model):
    task = models.ForeignKey(Task)
    place = models.ForeignKey(Place)


class PlaceProperty(models.Model):
    place = models.ForeignKey(Place)
    property = models.CharField(max_length=1000)


class Distance(models.Model):
    place_f = models.ForeignKey(Place, related_name='first')
    place_s = models.ForeignKey(Place, related_name='second')
    #distance = models.IntegerField()
    time = models.TimeField()