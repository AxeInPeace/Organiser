# from .models import Event, Task
import datetime
import random
import copy

POPULATION_SIZE = 100
NEW_GENERATION_SIZE = int(POPULATION_SIZE / 2)
WINDOW_SIZE = datetime.timedelta(hours=2)
ERA_AMOUNT = 500
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
        for event in events:
            self.events.append(event)
            self.full_info.append(event)
        self.left_border = self.events[0].start_time
        self.right_border = self.events[-1].end_time
        for task in tasks:
            cur_gene = self.__put_task_into_genome__(task)
            self.genes.append(cur_gene)
            self.full_info.append(cur_gene)
            self.full_info.sort(key=lambda k: k.start_time)


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

    def __choose_random_time__(self):
        delta = self.right_border - self.left_border
        rand_days = random.randint(0, delta.days)
        if rand_days == delta.days:
            rand_secs = random.randint(0, delta.seconds)
        else:
            rand_secs = random.randint(0, 86399)
        return self.left_border + datetime.timedelta(days=rand_days, seconds=rand_secs)

    def __deadline_satisfaction__(self):
        penalty = 0
        for gene in self.genes:
            if gene.end_time > gene.deadline:
                penalty += 1
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
    babys_genes = []
    for i in range(divider_place):
        babys_genes.append(copy.copy(par1.genes[i]))
    for i in range(divider_place, len(par2.genes)):
        babys_genes.append(copy.copy(par2.genes[i]))
    baby = Genome(par1.events, par1.genes)
    baby.genes = babys_genes
    return baby


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
        #cur_item = copy.copy(item)
        if random.random() < MUTATE_RATE:
            item.mutate()
            #if cur_item.fitness_function() > item.fitness_function():
                #item = cur_item



def natural_selection(population):
    population.sort(key=lambda k: k.fitness_function())
    for i in range(NEW_GENERATION_SIZE):
        population.pop()
    return population


def genetic(events, tasks):
    population = generate_population(events, tasks)

    for i in range(ERA_AMOUNT):
        roulette = form_roulette(population)
        new_generation = generate_new_population(roulette, population)
        mutate(new_generation)
        total_population = population + new_generation
        population = natural_selection(total_population)

    population.sort(key=lambda k: k.fitness_function())
    i = 0
    for task in tasks:
        task.start_time = population[0].genes[i].start_time
        task.end_time = population[0].genes[i].end_time
        task.save()
        i += 1
