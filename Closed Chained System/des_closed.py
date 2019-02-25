import random
import simpy

SEED = 42
average_processing_time = 0.25

response_times =[]
# queue_lengths = []
# waiting_times = []

concurrency = 100
num_cores = 4


def client(env, out_pipe, in_pipe, i):
    global response_times
    while True:
        processing_time = random.expovariate(1/average_processing_time)
        arrival_time = env.now
        d = {1: processing_time, 2: i, 3: arrival_time}
        out_pipe.put(d)
        response = yield in_pipe.get(filter=lambda x: True if x[2] == i else False)
        response_time = env.now - arrival_time
        response_times.append(response_time)


def server1(env, in_pipe, outpipe):
    # global queue_lengths
    # global  waiting_times
    while True:
        request = yield in_pipe.get()
        processing_time = request[1]
        # arrival_time = request[3]
        # waiting_time = env.now - arrival_time
        # waiting_times.append(waiting_time)
        # queue_length = len(in_pipe.items)
        # queue_lengths.append(queue_length)
        yield env.timeout(processing_time)
        outpipe.put(request)


random.seed(SEED)

environment = simpy.Environment()
in_pipe_1=simpy.Store(environment)
out_pipe=simpy.FilterStore(environment)

for i in range(concurrency):
    environment.process(client(environment, in_pipe_1, out_pipe, i))

for i in range(int(num_cores)):
    environment.process(server1(environment,in_pipe_1, out_pipe))


environment.run(1000)

response_times=[x*1000 for x in response_times]