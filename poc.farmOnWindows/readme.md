# Omniverse Farm on Windows (local)

Proof of concept for installing and running farm as standalone service on local windows machine.

## Prerequisites

* [Omniverse Launcher](https://docs.omniverse.nvidia.com/prod_launcher/prod_launcher/installing_launcher.html) installed.

## Setup

1. Setup Queue
    1. Install/launch Farm Queue (service) from Omniverse Launcher
    1. Configure Queue URL (for agents to connect. Also, this is base url for api endpoint)
    1. Navigate to Queue Management dashboard(s): 
        ```sh
        # http://<queue_url>/queue/management/ui/
        # http://<queue_url>/queue/management/dashboard
        http://localhost:8222/queue/management/ui/
        http://localhost:8222/queue/management/dashboard
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
1. Setup Agent
    1. Install/launch Farm Agent from Omniverse Launcher
    1. Connect Agent to Queue by configuring the Queue address (and clicking "Connect"):
        ```sh
        # http://<queue_url>
        http://localhost:8222
        ```
    1. Configure Job directories:
        ```
        C:\Users\nycjyp\Code\sandbox\omniverse\poc.farmOnWindows\agent\jobs\*
        ```
    1. Navigate to Job Management Dashboard: 
        ```sh
        # http://<agent_url>/agent/management/ui/
        http://localhost:8223/agent/management/ui/
        ```
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

## first job (simple command)

1. Create `hello-omniverse.kit` file in `hello-omniverse` folder within the configured `jobs` directory and copy and paste contents of [hello world example](https://docs.omniverse.nvidia.com/app_farm/app_farm/guides/creating_job_definitions.html#job-definition-schema-system-executables) (see [schema](https://docs.omniverse.nvidia.com/app_farm/app_farm/guides/creating_job_definitions.html#schema-reference))
1. Verify Job has been added by Getting list of jobs
    ```
    curl -X GET 'http://localhost:8223/agent/operator/available' \
        -H 'accept: application/json'
    ```
1. Submit task using `queue/management/tasks/submit` endpoint:
    ```
    curl -X POST "http://localhost:8222/queue/management/tasks/submit" \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        --data '{"user":"my-user-id","task_type":"hello-omniverse","task_args":{},"task_comment":"My first job!"}'
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
* Note, "echo" command was not found, so replaced with "systeminfo" and removed args.

## second job (simple python script)

## ISSUES

* getting echo not found error back from agent.
* when I add job directories

## Questions:

* where is api docs for queue? https://forums.developer.nvidia.com/t/farm-queue-management-api-documentation/237548
* how to package script and dependencies?
* how to verify when agents are registered for job?
* How do we distribute jobs to agents?