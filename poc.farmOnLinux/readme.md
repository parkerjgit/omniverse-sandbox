# Omniverse Farm on Local

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
1. Create boilerplate launch script
    ```
    cat << 'EOF' > /opt/ove/ov-farm-queue/queue.sh
    #!/bin/bash

    BASEDIR=$(dirname "$0")
    exec $BASEDIR/kit/kit $BASEDIR/apps/omni.farm.queue.headless.kit \
        --ext-folder $BASEDIR/exts-farm-queue \
        --/exts/omni.services.farm.management.tasks/dbs/task-persistence/connection_string=sqlite:///$BASEDIR//task-management.db
    EOF
    ```
1. Make queue script executable
    ```
    sudo chmod +x /opt/ove/ov-farm-queue/queue.sh
    ```
1. Start Queue
    ```
    ./queue.sh &
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
1. Create boilerplate launch script
    ```
    cat << 'EOF' > /opt/ove/ov-farm-agent/agent.sh
    #!/bin/bash

    BASEDIR=$(dirname "$0")
    exec $BASEDIR/kit/kit $BASEDIR/apps/omni.farm.agent.headless.kit \
    --ext-folder $BASEDIR/exts-farm-agent \
    --/exts/omni.services.farm.agent.operator/job_store_args/job_directories/0=$BASEDIR/jobs/* \
    --/exts/omni.services.farm.agent.controller/manager_host=http://localhost:8222 \
    --/exts/omni.services.farm.agent.operator/manager_host=http://localhost:8222
    EOF
    ```
1. Make agent script executable
    ```
    chmod +x /opt/ove/ov-farm-agent/agent.sh
    ```
1. Start agent
    ```
    ./agent.sh &
    ```
    * [Expected Error](https://docs.omniverse.nvidia.com/app_farm/app_farm/agent.html#output-log) if no supported GPU capacity: 
    ```
    2023-01-02 22:49:01 [2,349ms] [Error] [omni.services.farm.facilities.agent.capacity.managers.base] Failed to load capacities for omni.services.farm.facilities.agent.capacity.GPU: NVML Shared Library Not Found
    ```

## First Job (simple command)

