from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Q
from .models import *
from ..schedule.views import get_context, check_events
from ..schedule.models import Schedule, Event, EventRepetition, Place, Imported_Event


def friends_context(request):
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
    return context


def my_friends(request):
    return render(request, 'friends/friends.html', friends_context(request))


def friend(request, id):
    friend_info = UserInfo.objects.get(id=id)
    friend_user = friend_info.user
    try:
        FriendRelation.objects.get(Q(friend_f=request.user, friend_s=friend_user) |
                                   Q(friend_s=request.user, friend_f=friend_user))
    except:  # DoesNotExcist:

        context = {'friend': friend_info}
        return render(request, 'friends/no_friend_page.html', context)

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
    to_user = UserInfo.objects.get(id=int(id)).user
    FriendshipRequest.objects.update_or_create(from_friend=request.user, to_friend=to_user, declined=False)
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


def import_schedule(request):
    schedule_id = request.POST.get('schedule')
    cur_schedule = Schedule.objects.get(id=schedule_id)
    possible_events = Event.objects.filter(schedule=cur_schedule)

    events_to_copy = []
    for item in possible_events:
        if not request.POST.get(str(schedule_id) + '-' + str(item.id)) is None:
            events_to_copy.append(item)

    places_to_copy = []
    for item in events_to_copy:
        places_to_copy.append(item.place)

    checker = check_events(events_to_copy, request)
    if checker['is_correct']:
        new_schedule = Schedule.objects.create(name=cur_schedule.name,
                                               user=request.user,
                                               priority=cur_schedule.priority)
        print(request.POST.get('chain_import'))
        if request.POST.get('chain_import') is None:
            for event in events_to_copy:
                new_event = Event.objects.create(name=event.name,
                                                 schedule=new_schedule,
                                                 place=event.place)
                event_repetitions = EventRepetition.objects.filter(event=event)
                for repetition in event_repetitions:
                    EventRepetition.objects.create(event=new_event,
                                                   start_time=repetition.start_time,
                                                   end_time=repetition.end_time)
        else:
            for event in events_to_copy:
                new_event_ref = Imported_Event.objects.create(event=event,
                                                 schedule=new_schedule)
        for place in places_to_copy:
            Place.objects.create(name=place.name, user=request.user)
        return JsonResponse({'not_success': False})
    else:
        return JsonResponse({'not_success': True,
                             'created_event': checker['created_event'].name,
                             'my_event': checker['my_event'].name})


def export_schedule(request):
    return HttpResponseRedirect('/friends')

