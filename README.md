# RUDICS CLIENT WRITTEN IN PYTHON FOR TESTING

## Python version and Libraries
```
python >= 3.7
pip install -r requirements.txt
```

## Expected JSON result from server
```
{
    "command": "command -to -run",
    "cpus": 1,
    "memory": 1024,
    "gpus": 0
}
```

## Config Items (The default config settings are in rudics_client_defaults.conf)

### SYSTEM section (* Items signify the default)
only_when_idle [True/False*]
> Ensures the client only runs work when the host is idle

resume_after_idle_secs [Default 500]
> The number of seconds the system should be idle before resuming

suspend_when_not_idle_secs [Default 5]
> The number of seconds the system has NOT been idle before suspending work. This ensures we don't stop work if the mouse was hit with no intention of using the system

log_level [DEBUG, INFO*, WARNING, ERROR, CRITICAL]
> The level at which we should log.

log_max_size_mb [Default 100]
> The max size the log will be before it's rotated for archival purposes

log_max_rotation_count [Default 5]
> The max number of rotated logs to maintain before removing them

user_interaction_check_secs [Default 5]
> The interval at which we check if the system is idle or not

checkpoint_interval_mins [Default 10]
> The number of minutes after which we should send checkpoint data back to the server

launch_as_submitter [True/False*]
> Should we run the work as the user who submitted it? (This will fail if the host doesn't have an account for this user)

server_address [Default http://rudics_server]
> The web URL for the server or cache proxy to the server

server_callback_interval_secs [Default 5]
> How often we should send status updates and request work from the server in seconds

ignore_server_cert [True*/False]
> Set to true if you're using self signed certificates on your webserver.

### PARTITIONING Section (* Items signify the default)
partition_system [True*/False]
> Should we use multiple resources on the system (true) or treat the machine as a single resource (false). A true value will leverage the config items below

partition_max_cpus [1-x, Default 100%%]
> The number or percentage of CPUs we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value.

partition_max_memory [1-x, Default 100%%]
> The amount or percentage of Memory we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value.

partition_max_gpus [0-x, Default 100%%]
> The number or percentage of GPUs we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value. There is an assumption that if you specify a gpu, at least 1 cpu will be associated with the job
