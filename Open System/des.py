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
        processing_time = random.expovariate(1/average_processing_time)
        arrival_time = env.now
        d = {1: processing_time, 2:i, 3: arrival_time}
        out_pipe.put(d)


def server(env, in_pipe):
    global response_times
    while True:
        request = yield in_pipe.get()
        processing_time = request[1]
        arrival_time = request[3]
        # waiting_time = env.now - arrival_time
        # queue_length = len(in_pipe.items)
        yield env.timeout(processing_time)
        # print("waiting time = " + str(waiting_time)+", queue length =  "+str(queue_length))
        response_time = env.now - arrival_time
        # print("Now time: "+str(env.now)+" Arrival Time: "+str(arrival_time))
        response_times.append(response_time)


random.seed(SEED)
requests = 10000
environment = simpy.Environment()
pipe=simpy.Store(environment)
environment.process(packet_generator(environment, requests, pipe))
environment.process(server(environment,pipe))
environment.run()
response_times=[x*100000 for x in response_times]
print(response_times)