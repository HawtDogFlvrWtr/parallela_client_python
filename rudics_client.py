import argparse
import subprocess
import time
import configparser
import psutil
import os
import sys
import errno
import logging
import threading
import queue
import requests
import json
import math
import signal
from classes.gpu_detector import GPUDetector
from logging.handlers import RotatingFileHandler
#from dbus_idle import IdleMonitor

parser = argparse.ArgumentParser(description='Rudics client', epilog='Thanks for using this program!')
parser.add_argument('-c', '--config_path', help='The path to the client config file (rudics_client.conf)', default="rudics_client.conf")
parser.add_argument('-dc', '--default_config_path', help='The path to the client config file (rudics_client.conf)', default="rudics_client_defaults.conf")
parser.add_argument('-l', '--log_path', help="The path to the default log file", default='rudics_client.log')
args = parser.parse_args()
default_config_values = {}
temp_log_list = []
q = queue.Queue()
host_busy = False
exit_event = threading.Event()
threads = []

# Open and read default config
default_config = configparser.ConfigParser()
default_config.read(args.default_config_path)

# Opena nd read override config
config = configparser.ConfigParser()
config.read(args.config_path)

# Get a logger instance and possibles dictionary
logger = logging.getLogger(__name__)
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Config file doesn't exist
if not os.path.isfile(args.config_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.config_path)

# Config defaults file doesn't exist
if not os.path.isfile(args.default_config_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.default_config_path)

# Load default configs into memory
for section_name in default_config.sections():
    for key, value in default_config.items(section_name):
        if section_name not in default_config_values:
            default_config_values[section_name] = {key: value}
        else:
            default_config_values[section_name].update({ key: value })

# Iterate client configs and overwrite defaults
for section_name in config.sections():
    for key, value in config.items(section_name):
        if section_name not in default_config_values: # Handle users trying to make up sections in the config
            temp_log_list.append(f"Section {section_name} is invalid")
        elif key not in default_config_values[section_name]: # Handle users trying to make up keys in the configs
            temp_log_list.append(f"Key {key} in section {section_name} is invalid")
        else:
            default_config_values[section_name][key] = value

# Configure basic logging and rotation handler after config overrides
config_log_level = default_config_values['SYSTEM']['log_level'].upper()
api_key = default_config_values['SYSTEM']['api_key']
max_log_bytes = int(default_config_values['SYSTEM']['log_max_size_mb']) * 1_048_576
log_max_rotation_count = int(default_config_values['SYSTEM']['log_max_rotation_count'])
logger.setLevel(config_log_level)
handler = RotatingFileHandler(args.log_path, maxBytes=max_log_bytes, backupCount=log_max_rotation_count)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Iterate temp logs to 
for message in temp_log_list:
    logger.error(message)

def return_usable_resource(config_value, available_value, to_bytes=False):
    if '%' in config_value: # Convert string to decimal
        max_value = int(available_value) * (int(config_value.replace('%', '')) / 100)
        if to_bytes:
            return max_value * 1_048_576
        else:
            return max_value
    elif to_bytes: # handle MB designation
        max_value = int(config_value) * 1_048_576
        if max_value >= available_value:
            return available_value # defined max is greater than what we have, so set our current amount
    else:
        max_value = int(config_value)
        if max_value >= available_value:
            return available_value # defined max is greater than what we have, so set our current amount
        else:
            return max_value

# Determine System Facts
total_memory_bytes = psutil.virtual_memory().total
usable_memory_bytes = return_usable_resource(default_config_values['PARTITIONING']['partition_max_memory'], total_memory_bytes, to_bytes=True)

total_cpu_cores = psutil.cpu_count(logical=True)
usable_cpu_cores = return_usable_resource(default_config_values['PARTITIONING']['partition_max_cpus'], total_cpu_cores)

gpu_detector = GPUDetector()
total_gpus = gpu_detector.get_gpu_counts()['total_gpus']
usable_gpus = return_usable_resource(default_config_values['PARTITIONING']['partition_max_gpus'], total_gpus)

def signal_handler(signum, frame):
    """Handler for SIGINT (Ctrl+C)."""
    print("\nCtrl+C detected. Setting exit flag...")
    exit_event.set()

def callback_thread(q, url, interval, ignore_cert, api_key):
    global host_busy
    global usable_memory_bytes
    global usable_cpu_cores
    global usable_gpus
    print("Started callback thread")
    try:
        while not exit_event.is_set():
            logger.info(f"Available Resources: cpu - {usable_cpu_cores}, mem - {usable_memory_bytes}, gpus - {usable_gpus}")
            try:
                if ignore_cert.upper() == 'TRUE': # use the value from config to determine if we should ignore cert issues
                    verify_value = True
                else:
                    verify_value = False
                if usable_cpu_cores > 0:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Accept": "application/json",
                    }
                    url = f"{url}/api/get_jobs/?cpus={usable_cpu_cores}&mem={usable_memory_bytes}&gpu={usable_memory_bytes}"
                    response = requests.get(url, verify=verify_value, headers=headers)
                    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                    data = response.json()
                    if len(data) > 0: # Watch for a blank return meaning we have nothing to give
                        logger.debug(f"Successfully retrieved JSON data: {json.dumps(data)}")
                        for record in data:
                            for command in record['metadata']:
                                # Update the global values so everyone knows where we stand on resources
                                usable_cpu_cores -= command['cpus']
                                usable_memory_bytes -= command['memory']
                                usable_gpus -= command['gpus']
                                q.put(command) # Push the entire dictionary to the queue
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request Error: {e}")
            except requests.exceptions.JSONDecodeError:
                logger.error("Error: Could not decode JSON from the response.")
            time.sleep(int(interval))
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting gracefully.")
        # Perform any necessary cleanup here
        print("Cleanup complete.")

def thread_function(q, thread_num):
    global host_busy
    global usable_memory_bytes
    global usable_cpu_cores
    global usable_gpus
    print(f"Thread {thread_num} started")
    try:
        while not exit_event.is_set():
            queue_item = q.get()
            command = queue_item['command'] 
            # TODO: Need to do string replacement for cpu, memory, gpus in the command in case the user passes it to their app
            cpus = queue_item['cpus']
            mem = queue_item['memory']
            gpus = queue_item['gpus']
            process = subprocess.Popen(command.split(' '))
            p = psutil.Process(process.pid)
            try:
                while process.poll() is None: # Still running
                    if host_busy:
                        p.suspend()
                        children = p.children(recursive=True)
                        for child in children:
                            logger.info(f"Suspending child process: {child.pid} ({child.name()})")
                            child.suspend()
                    if not host_busy and p.status() == psutil.STATUS_STOPPED:
                        p.resume()
                        children = p.children(recursive=True)
                        for child in children:
                            logger.info(f"Resuming child process: {child.pid} ({child.name()})")
                            child.resume()
                    time.sleep(2)
            except psutil.NoSuchProcess:
                print(f"Process with PID {p} exited")
            # TODO: Capture cputime etc and send back to rudics server 
            logger.debug(f"{thread_num}: {queue_item}")
            usable_cpu_cores += cpus
            usable_memory_bytes +=  mem
            usable_gpus +=  gpus
            q.task_done()
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting gracefully.")
        # Perform any necessary cleanup here
        print("Cleanup complete.")

for thread_num in range(math.floor(usable_cpu_cores)): # Create threads equal to the total number of cores from the config
    producer_thread = threading.Thread(target=thread_function, args=(q, thread_num,))
    producer_thread.start()
    threads.append(producer_thread)

# Start requests thread
server_address = default_config_values['SYSTEM']['server_address']
callback_interval = default_config_values['SYSTEM']['server_callback_interval_secs']
ignore_server_cert = default_config_values['SYSTEM']['ignore_server_cert']

requests_thread = threading.Thread(target=callback_thread, args=(q, server_address, callback_interval, ignore_server_cert, api_key,))
requests_thread.start()
threads.append(requests_thread)

# Spin until we find an exit
check_idle_seconds = int(default_config_values['SYSTEM']['user_interaction_check_secs'])
resume_after_idle_secs = int(default_config_values['SYSTEM']['resume_after_idle_secs'])
suspend_when_not_idle_secs = int(default_config_values['SYSTEM']['suspend_when_not_idle_secs'])

# if we exit, we need to join the threads
for t in threads:
    t.join()