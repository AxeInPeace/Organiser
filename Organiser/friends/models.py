from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    def __str__(self):
        return self.name
    id = models.CharField(max_length=10, primary_key=True, auto_created=True)
    name = models.CharField(max_length=1000)
    user = models.OneToOneField(User)


class FriendRelation(models.Model):
    friend_f = models.ForeignKey(User, related_name='first')
    friend_s = models.ForeignKey(User, related_name='second')


class FriendshipRequest(models.Model):
    from_friend = models.ForeignKey(User, related_name='from_friend')
    to_friend = models.ForeignKey(User, related_name='to_friend')
    declined = models.BooleanField()

