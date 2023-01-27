# Omniverse Farm on Linux (Headless)

## Overview

1. Queue
    1. Install Queue (service)
    2. Configure Queue URL (for agents to connect. Also, this is base url for api endpoint)
    3. Navigate to dashboard at: `http://<queue_url>/queue/management/ui/`
2. Agent
    1. Install Agent
    1. Connect to Queue
    2. Configure Jobs directory (this is where scripts and kits go)
    3. Navigate to dashboard at: `http://<agent_url>/agent/management/ui/`

## Running Farm (after setup)

```
/opt/ove/ov-farm-queue/queue.sh &
/opt/ove/ov-farm-agent/agent.sh &
```

## Setup Queue

1. Install Dependencies
    ```
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
        libatomic1 \
        libxi6 \
        libxrandr2 \
        libxt6 \
        libegl1 \
        libglu1-mesa \
        libgomp1 \
        libsm6 \
        unzip
    ```
1. Instal Farm Queue package
    ```sh
    sudo mkdir -p /opt/ove/ov-farm-queue
    sudo curl https://d4i3qtqj3r0z5.cloudfront.net/farm-queue-launcher%40103.1.0%2Bmaster.33.956d9b7d.teamcity.linux-x86_64.release.zip --output /opt/ove/ov-farm-queue/farm-queue-launcher.zip
    sudo unzip /opt/ove/ov-farm-queue/farm-queue-launcher.zip
    sudo rm /opt/ove/ov-farm-queue/farm-queue-launcher.zip
    ```
1. Install the Kit SDK package
    ```sh
    sudo mkdir -p /opt/ove/ov-farm-queue/kit
    sudo curl https://d4i3qtqj3r0z5.cloudfront.net/kit-sdk-launcher@103.1%2Brelease.6024.1fc2e16c.tc.linux-x86_64.release.zip --output /opt/ove/ov-farm-queue/kit/kit-sdk-launcher.zip
    sudo unzip /opt/ove/ov-farm-queue/kit/kit-sdk-launcher.zip -d /opt/ove/ov-farm-queue/
    sudo rm /opt/ove/ov-farm-queue/kit/kit-sdk-launcher.zip
    ```
1. Recursively set owner of `ov-farm-queue` and subdirectories to non root user
    ```
    sudo chown -R josh:josh ov-farm-queue
    ```
1. Create launch script
    ```
    cat << 'EOF' > /opt/ove/ov-farm-queue/queue.sh
    #!/bin/bash

    BASEDIR=$(dirname "$0")
    exec $BASEDIR/kit/kit $BASEDIR/apps/omni.farm.queue.headless.kit \
        --ext-folder $BASEDIR/exts-farm-queue \
        --/exts/omni.services.farm.management.tasks/dbs/task-persistence/connection_string=sqlite:///$BASEDIR//task-management.db
    EOF
    ```
    * Note, Queue URL is automatically set to `http://localhost:8222`
1. Make queue script executable
    ```
    sudo chmod +x /opt/ove/ov-farm-queue/queue.sh
    ```
1. Start Queue
    ```
    ./queue.sh &
    ```
1. Navigate to Queue Management dashboard(s): 
    ```sh
    # http://<queue_url>/queue/management/ui/
    http://localhost:8222/queue/management/ui/
    ```
1. Find Queue Management API docs
    ```sh
    # http://<queue_url>/docs
    http://localhost:8222/docs
    ```
1. Perform health check
    ```
    curl -X GET 'http://localhost:8222/status' \
        -H 'accept: application/json'
    ```

## Setup Agent

1. Install Dependencies
    ```
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
        libatomic1 \
        libxi6 \
        libxrandr2 \
        libxt6 \
        libegl1 \
        libglu1-mesa \
        libgomp1 \
        libsm6 \
        unzip
    ```
1. Install Farm Agent Package
    ```
    sudo mkdir -p /opt/ove/ov-farm-agent
    sudo curl https://d4i3qtqj3r0z5.cloudfront.net/farm-agent-launcher%40103.1.0%2Bmaster.53.238d4340.teamcity.linux-x86_64.release.zip --output /opt/ove/ov-farm-agent/farm-agent-launcher.zip
    sudo unzip /opt/ove/ov-farm-agent/farm-agent-launcher.zip -d /opt/ove/ov-farm-agent/
    sudo rm /opt/ove/ov-farm-agent/farm-agent-launcher.zip
    ```
1. Install the Kit SDK package
    ```sh
    sudo mkdir -p /opt/ove/ov-farm-agent/kit
    sudo curl https://d4i3qtqj3r0z5.cloudfront.net/kit-sdk-launcher@103.1%2Brelease.6024.1fc2e16c.tc.linux-x86_64.release.zip --output /opt/ove/ov-farm-agent/kit/kit-sdk-launcher.zip
    sudo unzip /opt/ove/ov-farm-agent/kit/kit-sdk-launcher.zip -d /opt/ove/ov-farm-agent/kit/
    sudo rm /opt/ove/ov-farm-agent/kit/kit-sdk-launcher.zip
    ```
1. Recursively set owner of `ov-farm-agent` and subdirectories to non root user
    ```
    sudo chown -R josh:josh ov-farm-agent
    ```
1. Create launch script (configure jobs directory and queue host)
    ```
    cat << 'EOF' > /opt/ove/ov-farm-agent/agent.sh
    #!/bin/bash

    JOBSDIR="~/code/sandbox/omniverse-sandbox/poc.farmOnLinux/agent/jobs"
    exec $BASEDIR/kit/kit $BASEDIR/apps/omni.farm.agent.headless.kit \
    --ext-folder $BASEDIR/exts-farm-agent \
    --/exts/omni.services.farm.agent.operator/job_store_args/job_directories/0=$JOBSDIR/* \
    --/exts/omni.services.farm.agent.controller/manager_host=http://localhost:8222 \
    --/exts/omni.services.farm.agent.operator/manager_host=http://localhost:8222
    EOF
    ```
1. Make agent script executable
    ```
    chmod +x /opt/ove/ov-farm-agent/agent.sh
    ```
1. Start agent (in background)
    ```
    ./agent.sh &
    ```
    * [Expected Error](https://docs.omniverse.nvidia.com/app_farm/app_farm/agent.html#output-log) if no supported GPU capacity: 
    ```
    2023-01-02 22:49:01 [2,349ms] [Error] [omni.services.farm.facilities.agent.capacity.managers.base] Failed to load capacities for omni.services.farm.facilities.agent.capacity.GPU: NVML Shared Library Not Found
    ```
1. Navigate to Job Management Dashboard: 
    ```sh
    # http://<agent_url>/agent/management/ui/
    http://localhost:8223/agent/management/ui/
    ```
    * Note, this form simply edits the file specified by `job-spec-path` property (ie., Job definition path) in configured jobs directory. The effect is same as manually editing file, however not all [properties](https://docs.omniverse.nvidia.com/app_farm/app_farm/guides/creating_job_definitions.html#schema-reference) are exposed in form.
1. Find Agent Management API docs:
    ```sh
    # http://<agent_url>/docs
    http://localhost:8223/docs
    ```
1. Perform health check
    ```
    curl -X GET 'http://localhost:8223/status' \
        -H 'accept: application/json'
    ```

## Job: Hello World

1. [If you did NOT configure jobs directory to use repo] Copy `hello-omniverse` folder to configured jobs directory, e.g., `/opt/ove/ov-farm-agent/jobs`
    ```
    cp -R poc.farmOnLinux/agent/jobs/hello-omniverse /opt/ove/ov-farm-agent/jobs/hello-omniverse
    ```
    > **Notes**:
    > * `job type` property is set to "base" (ie., Command or executable) to allow execution of arbitrary shell commands or executable files.
    > * `command` property is set to name of shell command "echo". If we were executing a script, this would be the full path to script or executable.
    > * `args` (ie., Process arguments) are automatically passed
    > * `allowed_args` are passed by the client
1. [If nec] Restart agent to pick up job.
    ```
    kill -9 $(lsof -ti tcp:8223)
    ./agent.sh &
    ```
    > TODO: what is a better way to restart agent
1. [Optionally] Verify Job has been added by Getting list of jobs
    ```
    curl -X GET 'http://localhost:8223/agent/operator/available' \
        -H 'accept: application/json'
    ```
1. Submit task using `queue/management/tasks/submit` endpoint:
    ```
    curl -X POST "http://localhost:8222/queue/management/tasks/submit" \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        --data '{"user":"my-user-id","task_type":"hello-omniverse","task_args":{},"task_comment":"My job!"}'
    ```
1. Get Status of task:
    ```sh
    # of task with task id (returned when you submitted task)
    curl -X GET 'http://localhost:8222/queue/management/tasks/info/848973c4-5864-416b-976f-56a94cfc8258' \
        -H 'accept: application/json'
    
    # of all tasks matching type:
    curl -X GET 'http://localhost:8222/queue/management/tasks/list?task_type=hello-omniverse' \
        -H 'accept: application/json'
    ```

## Job: Run a Simple Python Script

1. [If you did NOT configure jobs directory to use repo] Copy `simple-python-script` folder to configured jobs directory, e.g., `/opt/ove/ov-farm-agent/jobs`
    ```sh
    cp -R poc.farmOnLinux/agent/jobs/simple-python-script /opt/ove/ov-farm-agent/jobs/simple-python-script
    ```
1. [If nec] Restart agent to pick up job.
    ```
    kill -9 $(lsof -ti tcp:8223)
    ./agent.sh &
    ```
1. [Optionally] Verify Job has been added by Getting list of jobs
    ```
    curl -X GET 'http://localhost:8223/agent/operator/available' \
        -H 'accept: application/json'
    ```
1. Submit task using `queue/management/tasks/submit` endpoint:
    ```
    curl -X POST "http://localhost:8222/queue/management/tasks/submit" \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        --data '{"user":"my-user-id","task_type":"simple-python-script","task_args":{"name":"Python Script"},"task_comment":"My job!"}'
    ```
1. Get Status of task:
    ```sh
    # of task with task id (returned when you submitted task)
    curl -X GET 'http://localhost:8222/queue/management/tasks/info/848973c4-5864-416b-976f-56a94cfc8258' \
        -H 'accept: application/json'
    
    # of all tasks matching type:
    curl -X GET 'http://localhost:8222/queue/management/tasks/list?task_type=simple-python-script' \
        -H 'accept: application/json'
    ```

## Questions

* How to get running agent to pick up changes to jobs without restarting service?
