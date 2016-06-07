from django.shortcuts import render, render_to_response, RequestContext
from .models import *
from .utils import *
from .genetic import genetic
from django.http import HttpResponseRedirect, JsonResponse
from itertools import chain


def get_context(request, user, date=datetime.datetime.now().date()):
    schedules = Schedule.objects.filter(user=user)
    places = Place.objects.filter(user=user)
    events = Event.objects.filter(schedule__in=schedules)
    events_to_change = events
    imported_events_ref = Imported_Event.objects.filter(schedule__in=schedules)
    imported_events = Event.objects.filter(id__in=imported_events_ref.values("event"))

    schedule_events = {}
    for schedule in schedules:
        schedule_events[schedule] = list(chain(events.filter(schedule=schedule),
                                         imported_events.filter(id__in=imported_events_ref.filter(schedule=schedule))))

    events = list(chain(events, imported_events))
    repetitions = EventRepetition.objects.filter(event__in=events)
    full_events = generate_events(repetitions, date)
    all_tasks = Task.objects.filter(user=user)
    tasks = all_tasks.filter(complete=False)

    full_tasks = generate_tasks(tasks, date)

    all_events = []
    for i in range(7):
        all_events.append(full_events[i] + full_tasks[i])
        all_events[i].sort(key=lambda k: k['start_time'])
    all_events = calc_all_height(all_events)

    days = [date + datetime.timedelta(i - date.weekday()) for i in range(7)]

    weekdays = [0, 1, 2, 3, 4, 5, 6]
    nowdate = datetime.datetime.now()
    context = {
        'schedules': schedules,
        'places': places,
        'schedule_events': schedule_events,
        'events': all_events,
        'events_to_change': events_to_change,
        'weekdays': weekdays,
        'tasks': tasks,
        'all_tasks': all_tasks,
        'nowdate': nowdate.date().strftime("%Y-%m-%d"),
        'days': days,
    }
    return context


def main(request):
    if request.user.is_authenticated():
        context = get_context(request, request.user)
        return render(request, 'schedule/schedule.html', context)
    else:
        return render(request, 'main_with_no_reg.html')


def render_table_schedule(request):
    to_date = datetime.date(int(request.GET.get('year')),
                            int(request.GET.get('month')) + 1,
                            int(request.GET.get('day')))
    if request.GET.get('user_id') is None:
        context = get_context(request, request.user, to_date)
    else:
        cur_user = User.objects.get(id=request.GET.get('user_id'))
        context = get_context(request, cur_user, to_date)
        context['no_generate'] = True
    return render_to_response('schedule/schedule_table.html',
                              context,
                              context_instance=RequestContext(request))


def add_task(request, task_id=None):
    name = request.POST.get('name')
    duration = get_duration(request.POST.get('duration'))
    deadline = get_datetime(request, 'deadline_date', 'deadline_time')
    place = request.POST.get('place')
    if task_id is None:
        cur_task = Task.objects.create(name=name,
                                       longitude=duration,
                                       user=request.user,
                                       deadline=deadline,
                                       complete=False)
    else:
        cur_task = Task.objects.get(id=task_id)
        cur_task.longitude = duration
        cur_task.user = request.user
        cur_task.deadline = deadline
        cur_task.complete = False
        cur_task.save()
    PlacesForTask.objects.create(task=cur_task, place_id=place)

    return JsonResponse({'success': True})


def add_event(request, event_id=None):
    name = request.POST.get('name')
    start_time = get_datetime(request, 'start_date', 'start_time')
    end_time = get_datetime(request, 'end_date', 'end_time')
    if correct_time(start_time, end_time):
        schedule = request.POST.get('schedule')
        place = request.POST.get('place')
        try:
            repetition_info = get_repetition_info(request)
            if event_id is None:
                cur_event = Event.objects.create(name=name, schedule_id=schedule, place_id=place)
            else:
                cur_event = Event.objects.get(id=event_id)
                cur_event.name = name
                cur_event.schedule_id = schedule
                cur_event.place_id = place
                cur_event.save()
            created_repetitions = []
            try:
                for j in range(repetition_info["amount"]):
                    start_date = start_time.date() + datetime.timedelta(j * 7)
                    end_date = end_time.date() + datetime.timedelta(j * 7)
                    for i in repetition_info["days"]:
                        if i - start_date.weekday() >= 0:
                            new_start_date = start_date + datetime.timedelta(i - start_date.weekday())
                            new_end_date = end_date + datetime.timedelta(i - start_date.weekday())
                        else:
                            new_start_date = start_date + datetime.timedelta(i - start_date.weekday() + 7)
                            new_end_date = end_date + datetime.timedelta(i - start_date.weekday() + 7)
                        new_start_time = datetime.datetime.combine(new_start_date, start_time.time())
                        new_end_time = datetime.datetime.combine(new_end_date, end_time.time())
                        created_repetitions.append(EventRepetition.objects.create(event=cur_event,
                                                   start_time=new_start_time,
                                                   end_time=new_end_time))
                checker = check_events([cur_event], request)
                if not checker['is_correct']:
                    for item in created_repetitions:
                        item.delete()
                    if event_id is None:
                        cur_event.delete()
                    return JsonResponse({'not_success': True,
                                         'created_event': checker['created_event'].name,
                                         'my_event': checker['my_event'].name})
            except:
                for item in created_repetitions:
                    item.delete()
                cur_event.delete()
                return JsonResponse({'not_success': True})

        except:
            return JsonResponse({'not_success': True})
    else:
        return JsonResponse({'not_success': True})
    if event_id is None:
        return JsonResponse({'not_success': False})
    return True  # success = True for change_event


def add_schedule(request):
    context = get_context(request, request.user)
    context['message'] = "Расписание успешно создано"
    if request.method == 'POST':
        name = request.POST.get('name')
        priority = request.POST.get('priority')
        try:
            Schedule.objects.create(user=request.user, name=name, priority=priority)
        except:
            context["message"] = "Ошибка при создании расписания"
    return render(request, 'schedule/schedule.html', context)


def add_place(request):
    name = request.GET.get('place_name')
    place = Place.objects.create(name=name, user=request.user)
    place_id = place.id
    return JsonResponse({'id': place_id})


def generate_shedule(request):
    schedules = Schedule.objects.filter(user=request.user)
    events = Event.objects.filter(schedule__in=schedules)
    imported_events_ref = Imported_Event.objects.filter(schedule__in=schedules)
    imported_events = Event.objects.filter(id__in=imported_events_ref.values("event"))
    events = list(chain(events, imported_events))
    repetitions = EventRepetition.objects.filter(event__in=events)

    tasks = list(Task.objects.filter(user=request.user, complete=False))
    genetic(list(repetitions), tasks)
    context = get_context(request, request.user)
    return render(request, 'schedule/schedule.html', context)


def change_task_status(request):
    task_id = int(request.GET.get('task_id'))
    cur_task = Task.objects.get(id=task_id)
    if cur_task.complete:
        cur_task.complete = False
    else:
        cur_task.complete = True
    cur_task.save()
    return JsonResponse({'complete': cur_task.complete})


def change_events(request):
    if request.method == 'POST':
        event_id = int(request.POST.get('event_id'))
        old_reps = list(EventRepetition.objects.filter(event_id=event_id))
        print(old_reps)
        success = add_event(request, event_id)
        if success == True:
            print(old_reps)
            for item in old_reps:
                item.delete()
            return JsonResponse({'not_success': False})
        else:
            return success


def change_schedules(request):
    if request.method == 'POST':
        schedule_id = int(request.POST.get('schedule_id'))
        cur_schedule = Schedule.objects.get(id=schedule_id)
        cur_schedule.name = request.POST.get('name')
        cur_schedule.priority = request.POST.get('priority')
        cur_schedule.save()
        return HttpResponseRedirect('/')


def delete_schedule(request):
    schedule_id = int(request.GET.get('schedule_id'))
    Schedule.objects.get(id=schedule_id).delete()
    Event.objects.filter(schedule_id = schedule_id).delete()
    Imported_Event.objects.filter(schedule_id = schedule_id).delete()
    return JsonResponse({})


def delete_event(request):
    event_id = int(request.GET.get('event_id'))
    Event.objects.get(id=event_id).delete()
    EventRepetition.objects.filter(event_id=event_id).delete()
    Imported_Event.objects.filter(event_id=event_id).delete()
    return JsonResponse({})


def change_tasks(request):
    if request.method == 'POST':
        task_id = int(request.POST.get('task_id'))
        Task.objects.get(id=task_id).delete()
        answer = add_task(request)
        context = get_context(request, request.user)
        tasks = Task.objects.filter(user=request.user)
        context["tasks"] = tasks
        return answer


def delete_task(request):
    task_id = int(request.GET.get('task_id'))
    Task.objects.get(id=task_id).delete()


def change_places(request):
    if request.method == 'POST':
        place_id = int(request.POST.get('place_change_id'))
        cur_place = Place.objects.get(id=place_id)
        cur_place.name = request.POST.get('place_name')
        cur_place.save()
    context = get_context(request, request.user)
    places = Place.objects.filter(user=request.user)
    context["places"] = places
    distances = {}
    for f_p in places:
        distances[f_p] = {}
        for s_p in places:
            if f_p != s_p:
                distances[f_p][s_p], created = Distance.objects.get_or_create(place_f=f_p,
                                                                              place_s=s_p,
                                                                              defaults={'time': datetime.timedelta()})
    context["dist"] = distances
    return render(request, 'schedule/places.html', context)


def delete_places(request):
    place_id = int(request.GET.get('place_id'))
    Place.objects.get(id=place_id).delete()


def time_for_places(request):
    fp = int(request.POST.get('time_place_1'))
    sp = int(request.POST.get('time_place_2'))
    dist = get_duration(request.POST.get('time_between_places'))
    Distance.objects.update_or_create(place_f_id=fp, place_s_id=sp, defaults={'time': dist})
    Distance.objects.update_or_create(place_s_id=fp, place_f_id=sp, defaults={'time': dist})
    context = get_context(request, request.user)
    places = Place.objects.filter(user=request.user)
    context["places"] = places
    distances = {}
    for f_p in places:
        distances[f_p] = {}
        for s_p in places:
            if f_p != s_p:
                distances[f_p][s_p], created = Distance.objects.get_or_create(place_f=f_p,
                                                                              place_s=s_p,
                                                                              defaults={'time': datetime.timedelta()})
    context["dist"] = distances
    return render(request, 'schedule/places.html', context)