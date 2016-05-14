from django.db import models
from django.contrib.auth.models import User


class Place(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=1000)
    user = models.ForeignKey(User)


class Schedule(models.Model):
    def __str__(self):
        return self.name
    user = models.ForeignKey(User)
    name = models.CharField(max_length=1000)
    priority = models.IntegerField()


class Event(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=1000)
    schedule = models.ForeignKey(Schedule)
    place = models.ForeignKey(Place)
    # period = models.DurationField()
    # amount = models.IntegerField()


class EventRepetition(models.Model):
    def __str__(self):
        return self.event.name + ' ' + str(self.start_time) + ' ' + str(self.end_time)
    event = models.ForeignKey(Event)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)


class Task(models.Model):
    def __str__(self):
        return self.name + ' ' + str(self.start_time) + ' ' + str(self.end_time)
    name = models.CharField(max_length=1000)
    user = models.ForeignKey(User)
    longitude = models.DurationField()
    deadline = models.DateTimeField()
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    complete = models.BooleanField(null=False, default=False)


class TaskHierarchy(models.Model):
    ancestor = models.ForeignKey(Task, related_name='ancestor')
    me = models.ForeignKey(Task, related_name='child')


class TaskRepetition(models.Model):
    task = models.ForeignKey(Task)
    repetition = models.DurationField()  # repeat every repetition time
    amount = models.IntegerField()       # how many times Task will repeat


class PlacesForTask(models.Model):
    task = models.ForeignKey(Task)
    place = models.ForeignKey(Place)


class PlaceProperty(models.Model):
    place = models.ForeignKey(Place)
    property = models.CharField(max_length=1000)


class Distance(models.Model):
    def __str__(self):
        return str(self.time)
    place_f = models.ForeignKey(Place, related_name='first')
    place_s = models.ForeignKey(Place, related_name='second')
    time = models.DurationField()
