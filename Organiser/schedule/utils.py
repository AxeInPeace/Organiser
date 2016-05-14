import datetime


def get_datetime(request, date_name, time_name):
    return datetime.datetime.strptime(request.POST.get(date_name) + request.POST.get(time_name), '%Y-%m-%d%H:%M')


def get_duration(time):
    cur_time = datetime.datetime.strptime(time, '%H:%M')
    return datetime.timedelta(minutes=cur_time.minute, hours=cur_time.hour)


def correct_time(time):
    try:
        if datetime.datetime(2016, 1, 1) < time < datetime.datetime(2116, 1, 1):
            return True
        else:
            return False
    except:
        return False


def get_repetition_info(request):
    amount = int(request.POST.get('amount'))
    if amount < 1:
        amount = 1
    repeat = int(request.POST.get('repeat'))
    if repeat is None:
        period = datetime.timedelta(0)
    else:
        period = datetime.timedelta(repeat)

    days = []
    for i in range(7):
        if request.POST.get('weekday'+str(i)) == str(i):
            days.append(i)
    rep = {
        'amount': amount,
        'days': days,
        'period': period,
        'cycles': len(days),
    }
    return rep


def get_event_day(start_day, weekday):
    start_weekday = start_day.weekday()
    if start_weekday <= weekday:
        new_start_day = start_day + datetime.timedelta(weekday - start_weekday)
    else:
        new_start_day = start_day + datetime.timedelta(weekday - start_weekday + 7)

    return new_start_day.date()


def event_dict_create(name, start_time, end_time, color="white"):
    return {
        'name': name,
        'start_time': start_time.time(),
        'end_time': end_time.time(),
        'height': 0,
        'space_before': 0,
        'color': color,
    }


def calc_height(event, before_event):
    time_diff = datetime.timedelta(hours=event['end_time'].hour - event['start_time'].hour,
                                   minutes=event['end_time'].minute - event['start_time'].minute)
    event['height'] = 100 * time_diff / datetime.timedelta(days=1)
    if before_event is None:
        before_event = event_dict_create("None", datetime.datetime(1, 1, 1), datetime.datetime(1, 1, 1))
    time_before = datetime.timedelta(hours=event['start_time'].hour - before_event['end_time'].hour,
                                     minutes=event['start_time'].minute - before_event['end_time'].minute)
    event['space_before'] = 100 * time_before / datetime.timedelta(days=1)


def generate_events(repetitions, cur_date=datetime.datetime.now().date()):
    cur_weekday = cur_date.weekday()
    dates = []
    for i in range(7):
        dates.append(cur_date + datetime.timedelta(i - cur_weekday))

    events_in_cur_week = []

    for rep in repetitions:
        if rep.start_time.date() in dates or rep.end_time.date() in dates:
            events_in_cur_week.append(rep)

    event_per_weekday = [[] for k in range(7)]

    for event in events_in_cur_week:
        if event.start_time.date() == event.end_time.date():
            event_per_weekday[event.start_time.weekday()].append(
                event_dict_create(event.event.name, event.start_time, event.end_time, 'green')
            )
        else:
            end_of_start_day = datetime.datetime.combine(event.start_time.date(), datetime.time(23, 59, 59))
            start_of_end_day = datetime.datetime.combine(event.end_time.date(), datetime.time(0, 0, 0))

            if end_of_start_day.date() in dates:
                event_per_weekday[end_of_start_day.weekday()].append(
                    event_dict_create(event.event.name, event.start_time, end_of_start_day, 'green')
                )

            if start_of_end_day.date() in dates:
                event_per_weekday[start_of_end_day.weekday()].append(
                    event_dict_create(event.event.name, start_of_end_day, event.end_time, 'green')
                )

    for i in range(7):
        event_per_weekday[i].sort(key=lambda k: k['start_time'])
        event_per_weekday[i].append(
            event_dict_create("None",
                              datetime.datetime(1, 1, 1, hour=23, minute=59, second=59),
                              datetime.datetime(1, 1, 1, hour=23, minute=59, second=59))
        )

    return event_per_weekday


def calc_all_height(all_events):
    for events in all_events:
        before_event = None
        for event in events:
            calc_height(event, before_event)
            before_event = event
    return all_events


def generate_tasks(tasks, cur_date=(datetime.datetime.now().date() + datetime.timedelta(0))):
    cur_weekday = cur_date.weekday()
    dates = []
    for i in range(7):
        dates.append(cur_date + datetime.timedelta(i - cur_weekday))

    tasks_in_cur_week = []

    for task in tasks:
        if not(task.start_time is None or task.end_time is None):
            task_date = task.start_time.date()
            if task_date in dates:
                tasks_in_cur_week.append(task)
            elif dates[0] - task_date == datetime.timedelta(1) \
                    and task.start_time.date() != task.end_time.date():
                tasks_in_cur_week.append(task)

    task_per_weekday = []
    for i in range(7):
        task_per_weekday.append([])

    for task in tasks_in_cur_week:
        if task.start_time.date() == task.end_time.date():
            task_per_weekday[task.start_time.weekday()].append(
                    event_dict_create(task.name,
                                      task.start_time,
                                      task.end_time,
                                      'blue')
            )
        else:
            start_day_end = datetime.datetime.combine(task.start_time.date(), datetime.time(23, 59, 59))
            end_day_start = datetime.datetime.combine(task.end_time.date(), datetime.time(0, 0, 0))

            if start_day_end.date() in dates:
                task_per_weekday[start_day_end.weekday()].append(
                        event_dict_create(task.name, task.start_time, start_day_end, 'blue')
                )

            if end_day_start.date() in dates:
                task_per_weekday[end_day_start.weekday()].append(
                        event_dict_create(task.name, end_day_start, task.end_time, 'blue')
                )

    for i in range(7):
        task_per_weekday[i].sort(key=lambda k: k['start_time'])
        task_per_weekday[i].append(
            event_dict_create("None",
                              datetime.datetime(1, 1, 1, hour=23, minute=59, second=59),
                              datetime.datetime(1, 1, 1, hour=23, minute=59, second=59))
        )

    return task_per_weekday


