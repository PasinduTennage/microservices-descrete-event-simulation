import random
import simpy


SEED = 42
average_processing_time = 0.25

response_times =[]
queue_lengths = []
waiting_times = []

concurrency = 100
num_cores = 4


def client(env, out_pipe, in_pipe, i):
    global response_times
    while True:
        processing_time_1 = random.expovariate(1 / average_processing_time)
        processing_time_2 = random.expovariate(1 / average_processing_time)
        processing_time_3 = random.expovariate(1 / average_processing_time)
        processing_time_4 = random.expovariate(1 / average_processing_time)
        arrival_time = env.now
        d = {1: processing_time_1, 2: processing_time_2, 3: i, 4: processing_time_3, 5: processing_time_4}
        out_pipe.put(d)
        response = yield in_pipe.get(filter=lambda x: True if x[3] == i else False)
        response_time = env.now - arrival_time
        response_times.append(response_time)


def server_1_1(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[1]
        yield env.timeout(processing_time)
        out_pipe.put(request)


def server_1_2(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        out_pipe.put(request)


def server_2_1(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[2]
        yield env.timeout(processing_time)
        out_pipe.put(request)


def server_2_2(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        out_pipe.put(request)


def server_3_1(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[4]
        yield env.timeout(processing_time)
        out_pipe.put(request)


def server_3_2(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        out_pipe.put(request)


def server_4(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[5]
        yield env.timeout(processing_time)
        out_pipe.put(request)


random.seed(SEED)

environment = simpy.Environment()
in_pipe_1 = simpy.Store(environment)
in_pipe_2 = simpy.Store(environment)
in_pipe_3 = simpy.Store(environment)
in_pipe_4 = simpy.Store(environment)
in_pipe_5 = simpy.Store(environment)
in_pipe_6 = simpy.Store(environment)
in_pipe_7 = simpy.Store(environment)

out_pipe = simpy.FilterStore(environment)

for i in range(concurrency):
    environment.process(client(environment, in_pipe_1, out_pipe, i))


for i in range(int(num_cores/2)):
    environment.process(server_1_1(environment, in_pipe_1, in_pipe_2))
    environment.process(server_1_2(environment, in_pipe_7, out_pipe))
    environment.process(server_2_1(environment, in_pipe_2, in_pipe_3))
    environment.process(server_2_2(environment, in_pipe_6, in_pipe_7))
    environment.process(server_3_1(environment, in_pipe_3, in_pipe_4))
    environment.process(server_3_2(environment, in_pipe_5, in_pipe_6))

for i in range(num_cores):
    environment.process(server_4(environment, in_pipe_4, in_pipe_5))

environment.run(1000)

response_times=[x*1000 for x in response_times]
waiting_times=[x*1000 for x in waiting_times]