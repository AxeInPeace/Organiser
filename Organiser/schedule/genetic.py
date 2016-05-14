# from .models import Event, Task
import datetime

import random
import copy

POPULATION_SIZE = 100
NEW_GENERATION_SIZE = int(POPULATION_SIZE / 2)
WINDOW_SIZE = datetime.timedelta(hours=2)
ERA_AMOUNT = 50
MUTATE_RATE = 0.1

DEADLINE_SATISFACTION_COEF = 100
PLACE_SATISFACTION_COEF = 5
SEQUENCE_SATISFACTION_COEF = 1


def time_distance(ev1, ev2):
    return ev2.start_time - ev1.end_time


class Gene(object):
    def __init__(self, st=datetime.datetime.now(), et=datetime.datetime.now(), lt=0, dd=0):
        self.start_time = st
        self.end_time = et
        self.longitude = lt
        self.deadline = dd

    def __str__(self):
        return str(self.start_time) + str(self.end_time)

    def set_start_time(self, st):
        self.start_time = st

    def set_end_time(self, et):
        self.end_time = et

    def set_time(self, st, et):
        self.start_time = st
        self.end_time = et


class Genome(object):
    def __init__(self, events, tasks):
        events.sort(key=lambda k: k.start_time)

        self.genes = []
        self.events = []
        self.full_info = []

        self.left_border = datetime.datetime.now(datetime.timezone.utc)
        for event in events:
            if event.start_time < self.left_border < event.end_time:
                self.left_border = event.end_time
                break

        self.full_info.append(Gene(self.left_border, self.left_border))

        for event in events:
            self.events.append(event)
            self.full_info.append(event)

        self.right_border = self.full_info[-1].end_time

        for task in tasks:
            cur_gene = self.__put_task_into_genome__(task)
            self.genes.append(cur_gene)
            self.full_info.append(cur_gene)
            self.full_info.sort(key=lambda k: k.start_time)

    def pair_with(self, other, divider):
        baby = Genome(self.events, self.genes)
        baby.genes = []
        for gene in self.genes[:divider + 1]:
            baby.genes.append(Gene(gene.start_time, gene.end_time, gene.longitude, gene.deadline))

        baby.full_info = []
        for event in baby.events:
            baby.full_info.append(event)
        for gene in baby.genes:
            baby.full_info.append(gene)
        baby.full_info.append(Gene(baby.left_border, baby.left_border))
        baby.full_info.sort(key=lambda k: k.start_time)

        for gene in other.genes[divider + 1:]:
            cur_gene = baby.__put_task_into_genome__(gene)
            baby.genes.append(cur_gene)
            baby.full_info.append(cur_gene)
            baby.full_info.sort(key=lambda k: k.start_time)
        #print('baby genes = ', len(baby.genes), '. baby full info = ', len(baby.full_info))
        return baby

    def __put_task_into_genome__(self, task):
        start_time, end_time = self.__find_nearest_time__(task)
        return Gene(start_time, end_time, task.longitude, task.deadline)

    def __find_nearest_time__(self, task):
        time = self.__choose_random_time__()
        for i in range(len(self.full_info) - 1):
            if self.full_info[i].end_time > time:
                if time_distance(self.full_info[i], self.full_info[i + 1]) > task.longitude:
                    return self.full_info[i].end_time, self.full_info[i].end_time + task.longitude
        return self.full_info[-1].end_time, self.full_info[-1].end_time + task.longitude

    def __make_task(self, task):
        for i in range(1, len(self.full_info)):
            if self.full_info[i].start_time > task.start_time:
                if time_distance(self.full_info[i - 1], self.full_info[i]) > task.longitude:
                    start_time, end_time =  self.full_info[i - 1].end_time, self.full_info[i - 1].end_time + task.longitude
                    return Gene(start_time, end_time, task.longitude, task.deadline)
        start_time, end_time = self.full_info[-1].end_time, self.full_info[-1].end_time + task.longitude
        return Gene(start_time, end_time, task.longitude, task.deadline)

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
        return 0

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
    #print('init lengths = ', len(population[0].genes), len(population[0].full_info))

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
