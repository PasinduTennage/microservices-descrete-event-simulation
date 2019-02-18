import random
import simpy

SEED = 42
arrival_rate = 25
average_processing_time = 0.025

response_times =[]


def packet_generator(env, number, out_pipe):
    for i in range(number):
        time_between_arrivals = random.expovariate(arrival_rate)
        yield env.timeout(time_between_arrivals)
        processing_time_1 = random.expovariate(1/average_processing_time)
        processing_time_2 = random.expovariate(1 / average_processing_time)
        processing_time_3 = random.expovariate(1 / average_processing_time)
        arrival_time = env.now
        d = {1: arrival_time, 2: processing_time_1, 3: processing_time_2, 4: processing_time_3}
        out_pipe.put(d)


def server_1(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[2]
        yield env.timeout(processing_time)
        out_pipe.put(request)


def server_2(env, in_pipe, out_pipe):
    while True:
        request = yield in_pipe.get()
        processing_time = request[3]
        yield env.timeout(processing_time)
        out_pipe.put(request)


def server_3(env, in_pipe):
    global response_times
    while True:
        request = yield in_pipe.get()
        processing_time = request[4]
        arrival_time = request[1]
        yield env.timeout(processing_time)
        response_time = env.now - arrival_time
        response_times.append(response_time)


random.seed(SEED)
requests = 10000
environment = simpy.Environment()
pipe_1 = simpy.Store(environment)
pipe_2 = simpy.Store(environment)
pipe_3 = simpy.Store(environment)
environment.process(packet_generator(environment, requests, pipe_1))
environment.process(server_1(environment,pipe_1, pipe_2))
environment.process(server_2(environment,pipe_2, pipe_3))
environment.process(server_3(environment,pipe_3))
environment.run()
response_times=[x*100000 for x in response_times]
print(response_times)
