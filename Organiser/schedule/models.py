from django.db import models
from django.contrib.auth.models import User


class Schedule(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(length=1000)
    priority = models.IntegerField()


class Event(models.Model):
    name = models.CharField(length=1000)
    schedule = models.ForeignKey(User)
    longitude = models.TimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class EventRepetition(models.Model):
    event = models.ForeignKey(Event)
    repetition = models.DurationField() #repeat every repetition time
    amount = models.IntegerField()      #how many times Task will repeat


class Task(models.Model):
    name = models.CharField(length=1000)
    user = models.ForeignKey(User)
    longitude = models.TimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class TaskRepetition(models.Model):
    task = models.ForeignKey(Task)
    repetition = models.DurationField() #repeat every repetition time
    amount = models.IntegerField()      #how many times Task will repeat


class PlacesForTask(models.Model):
    task = models.ForeignKey(Task)
    place = models.ForeignKey(Place)


class TaskHierarchy(models.Model):
    ancestor = models.ForeignKey(Task)
    me = models.ForeignKey(Task)


class Place(models.Model):
    name = models.CharField(length=1000)


class MtxDistances(models.Model):
    place_f = models.ForeignKey(Place)
    place_s = models.ForeignKey(Place)
    distance = models.IntegerField()
    time = models.TimeField()