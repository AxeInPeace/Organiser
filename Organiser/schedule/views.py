from django.shortcuts import render
from .models import *
from .utils import *
from .genetic import genetic


def get_context(request):
    schedules = Schedule.objects.filter(user=request.user)
    places = Place.objects.filter(user=request.user)
    events = Event.objects.filter(schedule__in=schedules)
    repetitions = EventRepetition.objects.filter(event__in=events)
    full_events = generate_events(repetitions)

    tasks = Task.objects.filter(user=request.user)
    full_tasks = generate_tasks(tasks)

    all_events = []
    for i in range(7):
        all_events.append(full_events[i] + full_tasks[i])
        all_events[i].sort(key=lambda k: k['start_time'])
    all_events = calc_all_height(all_events)

    weekdays = [0, 1, 2, 3, 4, 5, 6]
    context = {
        'schedules': schedules,
        'places': places,
        'events': all_events,
        'weekdays': weekdays,
        'tasks': tasks,
    }
    return context


def main(request):
    if request.user.is_authenticated():
        context = get_context(request)
        return render(request, 'schedule/schedule.html', context)
    else:
        return render(request, 'schedule/schedule.html')


def add_task(request):
    context = get_context(request)
    context['message'] = "Задача успешно создана"

    name = request.POST.get('name')
    duration = get_duration(request.POST.get('duration'))
    deadline = get_datetime(request, 'deadline_date', 'deadline_time')
    place = request.POST.get('place')

    cur_task = Task.objects.create(name=name, longitude=duration, user=request.user, deadline=deadline, start_time=datetime.datetime.now(), end_time=datetime.datetime.now())
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
            cur_event = Event.objects.create(name=name, schedule_id=schedule, start_time=start_time,
                                             end_time=end_time, place_id=place)
            try:
                for i in range(repetition_info["cycles"]):
                    print(get_start_day(start_time, repetition_info["days"][i]))
                    EventRepetition.objects.create(event=cur_event,
                                                   amount=repetition_info["amount"],
                                                   start_day=get_start_day(start_time, repetition_info["days"][i]),
                                                   repetition=repetition_info["period"])
            except:
                context['message'] = "Событие не может быть повторено"
                cur_event.delete()
        except:
            context['message'] = "Событие не может быть создано"

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
    name = request.POST.get('name')
    Place.objects.create(name=name, user=request.user)
    context = get_context(request)
    context['message'] = "Место успешно создано"
    return render(request, 'schedule/schedule.html', context)


def generate_shedule(request):
    schedules = Schedule.objects.filter(user=request.user)
    events = Event.objects.filter(schedule__in=schedules)
    #repetitions = EventRepetition.objects.filter(event__in=events)

    #full_events = generate_events(repetitions)
    tasks = list(Task.objects.filter(user=request.user))
    genetic(list(events), tasks)
    context = get_context(request)
    return render(request, 'schedule/schedule.html', context)
