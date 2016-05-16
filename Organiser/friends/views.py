from django.shortcuts import render, HttpResponseRedirect
from django.db.models import Q
from .models import *
from ..schedule.views import get_context

def my_friends(request):
    friends_f = FriendRelation.objects.filter(friend_f=request.user)
    friends_s = FriendRelation.objects.filter(friend_s=request.user)
    friends = []
    for man in friends_f:
        friends.append(UserInfo.objects.get(user=man.friend_s))
    for man in friends_s:
        friends.append(UserInfo.objects.get(user=man.friend_f))

    requests = []
    for item in FriendshipRequest.objects.filter(to_friend=request.user):
        requests.append(UserInfo.objects.get(user=item.from_friend))

    context = {
        'friends': friends,
        'requests': requests,
    }
    return render(request, 'friends/friends.html', context)


def friend(request, id):
    friend_info = UserInfo.objects.get(id=id)
    friend_user = friend_info.user
    context = get_context(request, friend_user)
    context['friend'] = friend_info
    return render(request, 'friends/friend_page.html', context)


def search_friends(request):
    string_to_search = request.POST.get('friend_search')
    found = UserInfo.objects.filter(Q(name__contains=string_to_search) | Q(id=string_to_search))
    context = {
        'people': found,
    }
    return render(request, 'friends/search_results.html', context)


def send_request(request, id):
    to_user = User.objects.get(id=id)
    FriendshipRequest.objects.create(from_friend=request.user, to_friend=to_user, declined=False)
    return HttpResponseRedirect('/friends')


def accept_request(request, id):
    FriendRelation.objects.create(friend_f=User.objects.get(id=id),
                                  friend_s=request.user)
    cur_request = FriendshipRequest.objects.get(from_friend=User.objects.get(id=id),
                                                to_friend=request.user)
    cur_request.delete()
    return HttpResponseRedirect('/friends')


def decline_request(request, id):
    cur_request = FriendshipRequest.objects.get(from_friend=User.objects.get(id=id),
                                                to_friend=request.user)
    cur_request.delete()
    return HttpResponseRedirect('/friends')
