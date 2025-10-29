import multiprocessing
import time
import random
import sys

def f():
    random_seconds = random.randint(10, 60)
    print(f"Running for {random_seconds} seconds")
    start_time = time.time()
    end_time = start_time + random_seconds
    while True:
        if time.time() >= end_time:
            break
        pass # An infinite loop that does nothing but consume CPU

if __name__ == "__main__":
    processes = []
    p = multiprocessing.Process(target=f)
    p.start()
    processes.append(p)
    
    p.join()
    print("Exited")