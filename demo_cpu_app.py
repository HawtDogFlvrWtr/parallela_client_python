import multiprocessing
import time
import random
import sys
import argparse

parser = argparse.ArgumentParser(description='parallela demo cpu consumer', epilog='Thanks for using this test app.')
parser.add_argument('--min', help='The path to the client config file (parallela_client.conf)', default=10, type=int)
parser.add_argument('--max', help='The path to the client config file (parallela_client.conf)', default=60, type=int)
parser.add_argument('--threads', help='The number of threads to launch the application with', default=1, type=int)
args, unknown = parser.parse_known_args()

def f(iter, min, max):
    print(f"Starting thread {iter}")
    random_seconds = random.randint(min, max)
    print(f"Running for {random_seconds} seconds")
    start_time = time.time()
    end_time = start_time + random_seconds
    while True:
        if time.time() >= end_time:
            break
        pass # An infinite loop that does nothing but consume CPU

if __name__ == "__main__":
    processes = []
    for i in range(args.threads):
        p = multiprocessing.Process(target=f, args=(i,args.min, args.max, ))
        p.start()
        processes.append(p)
    
    p.join()
    print("Exited")