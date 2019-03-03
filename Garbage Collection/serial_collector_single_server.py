import os
import random
import simpy
import numpy as np

def getLatencyList(filename):
    if os.path.isfile(filename):

        latencies = []
        with open(filename) as f:
            content = f.readlines()
            del content[0]
            del content[0]
            del content[0]
            for row in content:
                if(len(row.split(","))>1):
                    latency = row.split(",")[1][:-7].strip()
                    latencies.append(float(latency))
        return latencies

    else:
        print("File doesn't exists")
        return []

SEED = 42
average_processing_time = 0.0025

gc_times = getLatencyList("/home/pasindu/Project/WSO2/Results/GC_logs/prime/prime_GCLogs/GCLogs/1g_Heap_100_Users_UseSerialGC_collector_50_size_GCLog.txt")
max_heap_size = 1024
heap_per_request = 200
current_heap_usage = 0
response_times =[]
queue_lengths = []
waiting_times = []

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


def server(env, in_pipe, outpipe):
    global gc_times
    global max_heap_size
    global heap_per_request
    global current_heap_usage
    global response_times
    global queue_lengths
    global waiting_times

    while True:
        request = yield in_pipe.get()
        current_heap_usage = current_heap_usage+heap_per_request
        processing_time = request[1]
        arrival_time = request[3]
        waiting_time = env.now - arrival_time
        waiting_times.append(waiting_time)
        queue_length = len(in_pipe.items)
        queue_lengths.append(queue_length)
        yield env.timeout(processing_time)

        if current_heap_usage >= max_heap_size:
            gc_duration = gc_times[int(np.random.uniform(0, len(gc_times)))]*100
            yield env.timeout(gc_duration)
            current_heap_usage = 0
        outpipe.put(request)


random.seed(SEED)

environment = simpy.Environment()
in_pipe=simpy.Store(environment)
out_pipe=simpy.FilterStore(environment)

for i in range(concurrency):
    environment.process(client(environment, in_pipe, out_pipe, i))

for i in range(num_cores):
    environment.process(server(environment,in_pipe, out_pipe))

environment.run(1000)

response_times=[x*1000 for x in response_times]
waiting_times=[x*1000 for x in waiting_times]

print(response_times)