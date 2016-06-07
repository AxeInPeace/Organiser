from .models import PlacesForTask, Distance
import datetime

import random
import copy

POPULATION_SIZE = 100
NEW_GENERATION_SIZE = int(POPULATION_SIZE / 2)
WINDOW_SIZE = datetime.timedelta(hours=2)
ERA_AMOUNT = 10
MUTATE_RATE = 0.1

DEADLINE_SATISFACTION_COEF = 100
PLACE_SATISFACTION_COEF = 5
SEQUENCE_SATISFACTION_COEF = 1


def time_distance(ev1, ev2):
    if ev2.start_time > ev1.end_time:
        return ev2.start_time - ev1.end_time
    else:
        return datetime.timedelta()


def full_time_for_task(ev1, ev2, tsk_plc):
    try:
        ev1_tsk_time = Distance.objects.get(place_f_id=ev1.place, place_s=tsk_plc.place).time
    except:
        ev1_tsk_time = datetime.timedelta()
    if ev1_tsk_time.total_seconds() == 0:
        ev1_tsk_time = datetime.timedelta()

    try:
        tsk_ev2_time = Distance.objects.get(place_f_id=ev2.place, place_s=tsk_plc.place).time
    except:
        tsk_ev2_time = datetime.timedelta()
    if tsk_ev2_time.total_seconds() == 0:
        tsk_ev2_time = datetime.timedelta()
    return time_distance(ev1, ev2) - ev1_tsk_time - tsk_ev2_time, ev1_tsk_time


class Gene(object):
    def __init__(self, st=datetime.datetime.now(), et=datetime.datetime.now(), lt=0, dd=0, plc=None):
        self.start_time = st
        self.end_time = et
        self.longitude = lt
        self.deadline = dd
        self.place = plc

    def __str__(self):
        return self.place

    def set_start_time(self, st):
        self.start_time = st

    def set_end_time(self, et):
        self.end_time = et

    def set_time(self, st, et):
        self.start_time = st
        self.end_time = et


class Genome(object):
    def __init__(self, events, tasks, flag_init=True):
        self.genes = []
        self.events = []
        self.full_info = []
        self.left_border = datetime.datetime.now(datetime.timezone.utc)
        if events is None:
            return

        events.sort(key=lambda k: k.start_time)
        for event in events:
            if event.start_time < self.left_border < event.end_time:
                self.left_border = event.end_time
                break

        self.full_info.append(Gene(self.left_border, self.left_border))

        for event in events:
            if flag_init:
                event_gene = Gene(event.start_time,
                                  event.end_time,
                                  event.end_time - event.start_time,
                                  event.end_time,
                                  event.event.place
                                  )
            else:
                event_gene = event
            self.events.append(event_gene)
            self.full_info.append(event_gene)

        self.right_border = self.full_info[-1].end_time

        for task in tasks:
            cur_gene = self.__put_task_into_genome__(task, not flag_init)
            self.genes.append(cur_gene)
            self.full_info.append(cur_gene)
            self.full_info.sort(key=lambda k: k.start_time)

    def pair_with(self, other, divider):
        baby = Genome(self.events, self.genes, False)
        baby.genes = []
        for gene in self.genes[:divider + 1]:
            baby.genes.append(Gene(gene.start_time, gene.end_time, gene.longitude, gene.deadline, gene.place))

        baby.full_info = []
        for event in baby.events:
            baby.full_info.append(event)
        for gene in baby.genes:
            baby.full_info.append(gene)
        baby.full_info.append(Gene(baby.left_border, baby.left_border))
        baby.full_info.sort(key=lambda k: k.start_time)

        for gene in other.genes[divider + 1:]:
            cur_gene = baby.__put_task_into_genome__(gene, True)
            baby.genes.append(cur_gene)
            baby.full_info.append(cur_gene)
            baby.full_info.sort(key=lambda k: k.start_time)
        # print('baby genes = ', len(baby.genes), '. baby full info = ', len(baby.full_info))
        return baby

    def __put_task_into_genome__(self, task, pair=False):
        if pair:
            cur_place = task.place
        else:
            cur_place = PlacesForTask.objects.get(task=task)
        start_time, end_time = self.__find_nearest_time__(task, cur_place)
        return Gene(start_time, end_time, task.longitude, task.deadline, cur_place)

    def __find_nearest_time__(self, task, task_place=None):
        if task_place is None:
            task_place = task.place
        time = self.__choose_random_time__()
        for i in range(len(self.full_info) - 1):
            if self.full_info[i].end_time > time:
                time_for_task, time_for_travel = full_time_for_task(self.full_info[i],
                                                                    self.full_info[i + 1],
                                                                    task_place)
                if time_for_task >= task.longitude:
                    return self.full_info[i].end_time + time_for_travel, \
                           self.full_info[i].end_time + task.longitude + time_for_travel
        time_for_task, time_for_travel = full_time_for_task(self.full_info[-1], self.full_info[-1], task_place)
        return self.full_info[-1].end_time + time_for_travel, \
               self.full_info[-1].end_time + task.longitude + time_for_travel

    def __make_task(self, task):
        for i in range(1, len(self.full_info)):
            if self.full_info[i].start_time > task.start_time:
                time_for_task, time_for_travel = full_time_for_task(self.full_info[i - 1],
                                                                    self.full_info[i + 1],
                                                                    task.place)
                if time_for_task > task.longitude:
                    start_time = self.full_info[i - 1].end_time + time_for_travel
                    end_time = self.full_info[i - 1].end_time + task.longitude + time_for_travel
                    return Gene(start_time, end_time, task.longitude, task.deadline, task.place)
        time_for_task, time_for_travel = full_time_for_task(self.full_info[-1], self.full_info[-1], task.place)
        start_time, end_time = self.full_info[-1].end_time + time_for_travel, \
                               self.full_info[-1].end_time + task.longitude + time_for_travel
        return Gene(start_time, end_time, task.longitude, task.deadline, task.place)

    def __choose_random_time__(self):
        delta = self.right_border - self.left_border
        rand_days = random.randint(0, delta.days)
        if rand_days == delta.days:
            rand_secs = random.randint(0, delta.seconds)
        else:
            rand_secs = random.randint(0, 24 * 60 * 60 - 1)
        return self.left_border + datetime.timedelta(days=rand_days, seconds=rand_secs)

    def __deadline_satisfaction__(self):
        penalty = 0
        for gene in self.genes:
            if gene.end_time > gene.deadline:
                penalty += 1
                days_diff = gene.end_time - gene.deadline
                penalty += 0.5 * days_diff.days
        return penalty

    def __place_satisfaction__(self):
        penalty = 0
        for i in range(1, len(self.full_info) - 1):
            if self.full_info[i - 1].place != self.full_info[i].place:
                penalty += 1
        return penalty

    def __sequence_satisfaction__(self):
        penalty = 0
        for i in range(len(self.full_info) - 1):
            if time_distance(self.full_info[i], self.full_info[i + 1]) > WINDOW_SIZE:
                penalty += 1
        return penalty

    def mutate(self):
        rand_place = random.randint(0, len(self.genes) - 1)
        rand_task = self.genes[rand_place]
        new_time_start, new_time_end = self.__find_nearest_time__(rand_task)
        rand_task.set_time(new_time_start, new_time_end)

    def fitness_function(self):
        return DEADLINE_SATISFACTION_COEF * self.__deadline_satisfaction__() + \
               PLACE_SATISFACTION_COEF * self.__place_satisfaction__() + \
               SEQUENCE_SATISFACTION_COEF * self.__sequence_satisfaction__()

    def __lt__(self, other):
        return self.fitness_function() < other.fitness_function()

    def __gt__(self, other):
        return self.fitness_function() > other.fitness_function()

    def __le__(self, other):
        return self.fitness_function() <= other.fitness_function()

    def __ge__(self, other):
        return self.fitness_function() >= other.fitness_function()

    def __eq__(self, other):
        return self.fitness_function() == other.fitness_function()

    def __ne__(self, other):
        return self.fitness_function() != other.fitness_function()


def generate_population(events, tasks):
    population = []
    for i in range(POPULATION_SIZE):
        population.append(Genome(events, tasks))
    return population


def form_roulette(population):
    roulette = []
    fitness_sum = 0
    for item in population:
        cur_item_fit = item.fitness_function()
        roulette.append(cur_item_fit)
        fitness_sum += cur_item_fit
    roulette[0] /= fitness_sum
    for i in range(1, len(population) - 1):
        roulette[i] = roulette[i - 1] + roulette[i] / fitness_sum
    roulette[-1] = 1
    return roulette


def pairing(par1, par2):
    divider_place = random.randint(0, len(par1.genes) - 1)
    return par1.pair_with(par2, divider_place)


def choose_parant(roulette, population, rand):
    for i in range(len(roulette)):
        if roulette[i] >= rand:
            return population[i]


def generate_new_population(roulette, population):
    new_generation = []
    for i in range(NEW_GENERATION_SIZE):
        parant1 = choose_parant(roulette, population, random.random())
        parant2 = choose_parant(roulette, population, random.random())
        new_generation.append(pairing(parant1, parant2))
    return new_generation


def mutate(population):
    for item in population:
        cur_item = copy.copy(item)
        if random.random() < MUTATE_RATE:
            item.mutate()
            if cur_item.fitness_function() > item.fitness_function():
                item = cur_item


def natural_selection(population):
    population.sort(key=lambda k: k.fitness_function())
    for i in range(NEW_GENERATION_SIZE):
        population.pop()
    return population


def genetic(events, tasks):
    population = generate_population(events, tasks)
    for item in population:
        print(item.fitness_function())
    # print('init lengths = ', len(population[0].genes), len(population[0].full_info))

    for i in range(ERA_AMOUNT):
        roulette = form_roulette(population)
        new_generation = generate_new_population(roulette, population)
        mutate(new_generation)
        total_population = population + new_generation
        population = natural_selection(total_population)
        # print(population[0].fitness_function())

    population.sort(key=lambda k: k.fitness_function())
    i = 0
    print(population[0].fitness_function())
    for task in tasks:
        task.start_time = population[0].genes[i].start_time
        task.end_time = population[0].genes[i].end_time
        task.save()
        i += 1
