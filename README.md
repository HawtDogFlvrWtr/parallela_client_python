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
only_when_idle
> Ensures the client only runs work when the host is idle [True/False*]

resume_after_idle_secs
> The number of seconds the system should be idle before resuming [Default 500]

suspend_when_not_idle_secs [Default 5]
> The number of seconds the system has NOT been idle before suspending work. This ensures we don't stop work if the mouse was hit with no intention of using the system

log_level
> The level at which we should log. [DEBUG, INFO*, WARNING, ERROR, CRITICAL]

log_max_size_mb
> The max size the log will be before it's rotated for archival purposes [Default 100]

log_max_rotation_count
> The max number of rotated logs to maintain before removing them [Default 5]

user_interaction_check_secs
> The interval at which we check if the system is idle or not [Default 5]

checkpoint_interval_mins
> The number of minutes after which we should send checkpoint data back to the server [Default 10]

launch_as_submitter
> Should we run the work as the user who submitted it? (This will fail if the host doesn't have an account for this user) [True/False*]

server_address
> The web URL for the server [Default http://rudics_server]

server_callback_interval_secs
> How often we should send status updates and request work from the server in seconds [Default 5]

ignore_server_cert
> Set to true if you're using self signed certificates on your webserver. [True*/False]

### PARTITIONING Section (* Items signify the default)
partition_system
> Should we use multiple resources on the system (true) or treat the machine as a single resource (false). A true value will leverage the config items below [True*/False]

partition_max_cpus
> The number or percentage of CPUs we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value. [1-x, Default 100%%]

partition_max_memory
> The amount or percentage of Memory we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value. [1-x, Default 100%%]

partition_max_gpus
> The number or percentage of GPUs we should use on this system for jobs. For percentage values, a second % symbol should be used to escape the value. [1-x, Default 100%%]
