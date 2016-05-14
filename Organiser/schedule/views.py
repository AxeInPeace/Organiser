from django.shortcuts import render, render_to_response, RequestContext
from .models import *
from .utils import *
from .genetic import genetic
from django.http import HttpResponseRedirect, JsonResponse



def get_context(request, date=datetime.datetime.now().date()):
    schedules = Schedule.objects.filter(user=request.user)
    places = Place.objects.filter(user=request.user)
    events = Event.objects.filter(schedule__in=schedules)
    repetitions = EventRepetition.objects.filter(event__in=events)
    full_events = generate_events(repetitions, date)
    tasks = Task.objects.filter(user=request.user, complete=False)
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
        'events': all_events,
        'weekdays': weekdays,
        'tasks': tasks,
        'nowdate': nowdate.date().strftime("%Y-%m-%d"),
        'days': days,
    }
    return context


def main(request):
    if request.user.is_authenticated():
        context = get_context(request)
        return render(request, 'schedule/schedule.html', context)
    else:
        return render(request, 'schedule/schedule.html')


def table_schedule(request):
    to_date = datetime.date(int(request.GET.get('year')),
                            int(request.GET.get('month')) + 1,
                            int(request.GET.get('day')))
    context = get_context(request, to_date)
    return render_to_response('schedule/schedule_table.html',
                              context,
                              context_instance=RequestContext(request))


def add_task(request):
    context = get_context(request)
    context['message'] = "Задача успешно создана"

    name = request.POST.get('name')
    duration = get_duration(request.POST.get('duration'))
    deadline = get_datetime(request, 'deadline_date', 'deadline_time')
    place = request.POST.get('place')

    cur_task = Task.objects.create(name=name,
                                   longitude=duration,
                                   user=request.user,
                                   deadline=deadline,
                                   complete=False)
    PlacesForTask.objects.create(task=cur_task, place_id=place)

    return render(request, 'schedule/schedule.html', context)


def add_event(request):
    context = get_context(request)
    context['message'] = "Событие успешно создано"
    name = request.POST.get('name')
    start_time = get_datetime(request, 'start_date', 'start_time')
    end_time = get_datetime(request, 'end_date', 'end_time')
    if correct_time(start_time) and correct_time(end_time):
        schedule = request.POST.get('schedule')
        place = request.POST.get('place')
        try:
            repetition_info = get_repetition_info(request)
            cur_event = Event.objects.create(name=name, schedule_id=schedule, place_id=place)
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
            except:
                context['message'] = "Событие не может быть повторено"
                for item in created_repetitions:
                    item.delete()
                cur_event.delete()
                return render(request, 'schedule/schedule.html', context)

        except:
            context['message'] = "Событие не может быть создано"
            return render(request, 'schedule/schedule.html', context)
    else:
        context['message'] = "Неверный промежуток времени"
    return render(request, 'schedule/schedule.html', context)


def add_schedule(request):
    context = get_context(request)
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
    repetitions = EventRepetition.objects.filter(event__in=events)

    tasks = list(Task.objects.filter(user=request.user, complete=False))
    genetic(list(repetitions), tasks)
    context = get_context(request)
    return render(request, 'schedule/schedule.html', context)


def task_complete(request):
    task_id = int(request.GET.get('task_id'))
    cur_task = Task.objects.get(id=task_id)
    cur_task.complete = True
    cur_task.save()


def change_events(request):
    if request.method == 'GET':
        context = get_context(request)
        schedules = Schedule.objects.filter(user=request.user)
        events = Event.objects.filter(schedule__in=schedules)
        context["events"] = events
        return render(request, 'schedule/events.html', context)
    if request.method == 'POST':
        event_id = int(request.POST.get('event_id'))
        Event.objects.get(id=event_id).delete()
        EventRepetition.objects.filter(event_id=event_id).delete()
        add_event(request)
        return HttpResponseRedirect('/')


def get_event(request):
    event_id = int(request.GET.get('event_id'))
    event = Event.objects.get(id=event_id)
    repetitions = EventRepetition.objects.filter(event=event)


def delete_event(request):
    event_id = int(request.GET.get('event_id'))
    Event.objects.get(id=event_id).delete()
    EventRepetition.objects.filter(event_id=event_id).delete()


def change_tasks(request):
    if request.method == 'POST':
        task_id = int(request.POST.get('task_id'))
        Task.objects.get(id=task_id).delete()
        add_task(request)
    context = get_context(request)
    tasks = Task.objects.filter(user=request.user)
    context["tasks"] = tasks
    return render(request, 'schedule/tasks.html', context)


def delete_task(request):
    task_id = int(request.GET.get('task_id'))
    Task.objects.get(id=task_id).delete()


def change_places(request):
    if request.method == 'POST':
        place_id = int(request.POST.get('place_change_id'))
        Place.objects.get(id=place_id).delete()
        name = request.POST.get('place_name')
        Place.objects.create(name=name, user=request.user)
    context = get_context(request)
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
    Distance.objects.update_or_create(place_f_id=fp, place_s_id=sp, defaults={'time':dist})
    Distance.objects.update_or_create(place_s_id=fp, place_f_id=sp, defaults={'time':dist})
    context = get_context(request)
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