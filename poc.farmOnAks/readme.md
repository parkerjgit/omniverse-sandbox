# Omniverse farm on Aks

## Getting Started

## Stack

* Omniverse Services/Applications:
    * Farm
* Terraform - for provisioning infrasture
* Docker - container virtualization
* Kubernetes - container orchestration
* NVIDIA device plugin for Kubernetes - req. to run GPU enabled containers in your Kubernetes cluster.
* Helm - Package Manager for Kubernetes
* Azure Services
    * AKS

## Prerequisites

* [Omniverse farm ~~prerequisites~~ recommendations](https://docs.omniverse.nvidia.com/app_farm/app_farm/omniverse_farm_cloud_setup.html#prerequisites)
    * Two types of node configurations are needed: Farm services and farm workers.
    * Recommended: 
        * Farm containers are currently very large (improvements are coming) with a couple of gigs, and your local system storage would need to support that. We tend to run with 100GB file systems size.
        * Farm services: 
            * 3 x the equivalent of an t3.large (ie., 2vCPU, 8GB of Ram)
        * Farm Workers:
            * Kubernetes >= 1.24. Must be supported by the GPU operator (min = 1.16)
            * support the NVIDIA drivers, device plugin and container toolkit and have the GPU Operator installed on them. 
            * For OV based GPU workloads they'll need to be RTX enabled GPUs for best results. 

* [NVIDIA device plugin prerequisites](https://github.com/NVIDIA/k8s-device-plugin#prerequisites):
    * NVIDIA drivers ~= 384.81
    * nvidia-docker >= 2.0 || nvidia-container-toolkit >= 1.7.0 (>= 1.11.0 to use integrated GPUs on Tegra-based systems)
    * nvidia-container-runtime configured as the default low-level runtime
    * Kubernetes version >= 1.10

* [NVIDIA Container Toolkit prerequisites]():
    * GNU/Linux x86_64 with kernel version > 3.10
    * Docker >= 19.03 (recommended, but some distributions may include older versions of Docker. The minimum supported version is 1.12)
    * NVIDIA GPU with Architecture >= Kepler (or compute capability 3.0)
    * NVIDIA Linux drivers >= 418.81.07 (Note that older driver releases or branches are unsupported.)

## Setup

### 1. Deploy Kubernetes Cluster

> TODO: Verify that version of k8s is supported by farm (ie., >= 1.16, >= 1.24 recommended)

1. Configure resources to be created.
    1. Create `/infra-compute/terraform.tfvars` file:
        ```
        resource_group_name = "saz-resources"
        ssh_public_key      = "~/.ssh/id_rsa.pub"
        ``` 
    * Notes, 
        * if you don't have an ssh key pair, [create one](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/ssh-from-windows#create-an-ssh-key-pair)
        * add "GPU" node label to nodes in node pool, so that we can easily target them by label (when we install nvidia device plugin)
1. Create cloud resources
    1. Initialize terraform and provision cloud resources. 
        ```sh
        # from `/infra-compute` directory:
        terraform init
        terraform plan
        terraform apply
        ```
1. Perform sanity checks
    1. connect to cluster
        ```
        az aks get-credentials \
            --resource-group "dt-sandbox-resources" \
            --name "ovfarm-dev-aks-cluster"
        ```
    1. inspect cluster
        ```
        kubectl get all
        kubectl describe svc kubernetes
        ```

### 2a. Deploy Node Pool from image (Recommended)

1. Update your cluster to use the AKS GPU image 
    1. Install aks preview extension
        ```
        az extension add --name aks-preview
        az extension update --name aks-preview
        ```
    1. Register the GPUDedicatedVHDPreview feature (enables feature flag)
        ```
        az feature register --namespace "Microsoft.ContainerService" --name "GPUDedicatedVHDPreview"
        az feature show --namespace "Microsoft.ContainerService" --name "GPUDedicatedVHDPreview"
        ```
    1. Register provider (hack to propage the change)
        ```
        az provider register --namespace Microsoft.ContainerService
        ```
1. Deploy node pool
    ```
    az aks nodepool add \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool \
        --node-count 1 \
        --node-vm-size Standard_NV12ads_A10_v5 \
        --node-taints sku=gpu:NoSchedule \
        --aks-custom-headers UseGPUDedicatedVHD=true \
        --enable-cluster-autoscaler \
        --min-count 1 \
        --max-count 3 \
        --os-sku Ubuntu \
        --mode User \
        --labels vm_type=GPU
    ```
. Verify that GPUs are schedulable
    ```
    kubectl get nodes
    kubectl describe node <node_name>
    ```
    * Should see "nvidia.com/gpu" listed under "Capacity"
1. Run a sample GPU workload
    ```sh
    kubectl apply -f ./jobs/samples-tf-mnist-demo.yaml
    ```
1. Get job status
    ```
    kubectl get jobs samples-tf-mnist-demo --watch
    ```1
1. Get logs
    ```
    kubectl get pods --selector app=samples-tf-mnist-demo
    kubectl logs <pod_name>
    ````
1. [optionally] Update nodepool e.g. to add labels (expensive to recreate)
    ```
    az aks nodepool update \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool \
        --node-taints "" \
        --labels vm_type=GPU 
    ```
1. [optionally] Delete and re-deploy eg., to change vm-size
    ```
    az aks nodepool delete \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool
    az aks nodepool add ... (see Deploy node pool above)
    ```
1. [optionally] Clean-up resources
    ```
    az aks nodepool delete \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool
    ```

### 2b. Deploy GPU Node Pool from Daemonset

tbd...

### 3. Deploy Farm

1. Prerequisites
    1. NGC CLI 
        1. windows - download from https://ngc.nvidia.com/setup/installers/cli
        1. wsl/linux (amd64):
            ```
            wget --content-disposition https://ngc.nvidia.com/downloads/ngccli_linux.zip && unzip ngccli_linux.zip && chmod u+x ngc-cli/ngc
            find ngc-cli/ -type f -exec md5sum {} + | LC_ALL=C sort | md5sum -c ngc-cli.md5
            echo "export PATH=\"\$PATH:$(pwd)/ngc-cli\"" >> ~/.bash_profile && source ~/.bash_profile
            ngc --version
            ```
    1. NGC API Key
        1. generate from https://ngc.nvidia.com/setup
        1. login to ngc from cli with API Key
            ```
            ngc config set
            ````
    1. K8s Cluster
1. connect to cluster
    ```
    az aks get-credentials \
        --resource-group "dt-sandbox-resources" \
        --name "ovfarm-dev-aks-cluster"
    ```
1. Define variables
    ```
    K8S_NAMESPACE="ovfarm"
    NGC_API_KEY=<NGC_API_TOKEN>
1. Create namespace
    ```
    kubectl create namespace $K8S_NAMESPACE
    ```
    * Question: can this be default namespace?
1. Create [Docker Config Secret](https://kubernetes.io/docs/concepts/configuration/secret/#docker-config-secrets)
    ```
    kubectl create secret docker-registry my-registry-secret \
        --namespace $K8S_NAMESPACE \
        --docker-server="nvcr.io" \
        --docker-username='$oauthtoken' \
        --docker-password=$NGC_API_KEY
    ```
1. fetch helm chart
    ```
    helm fetch https://helm.ngc.nvidia.com/nvidia/omniverse/charts/omniverse-farm-0.3.2.tgz \
        --username='$oauthtoken' \
        --password=$NGC_API_KEY
    ```
1. configure deployment. besure to use correct dns zone for host in `values.yaml` file. Can get DNS Zone Name with:
    ```sh
    az aks show 
        --resource-group "ov-resources" 
        --name "ovfarm-dev-aks-cluster" 
        --query addonProfiles.httpApplicationRouting.config.HTTPApplicationRoutingZoneName 
    ```
1. install farm
    ```
    helm upgrade \
        --install \
            omniverse-farm \
            omniverse-farm-0.3.2.tgz \
        --create-namespace \
        --namespace $K8S_NAMESPACE \
        --values ./containers/farm/values.yaml
    helm list -n ovfarm
    ```
1. [optionally] update deployment
    ```
    helm upgrade --values ./containers/farm/values.yaml omniverse-farm omniverse-farm-0.3.2.tgz --namespace ovfarm
    ```
1. Validate the installation.
    1. Check that Pods are running
        ```sh
        kubectl get pods -o wide $K8S_NAMESPACE
        ```
    1. Ensure all pods in ready state
        ```sh
        kubectl -n $K8S_NAMESPACE wait --timeout=300s --for condition=Ready pods --all
        
        ```
        * Note, controller takes a very long time to initialize
    1. Check for errors for any pod that aren't ready
        ```sh
        kubectl describe pod <pod_name>
        ```
    1. Check endpoints with curl pod
        1. [run curl pod](https://kubernetes.io/docs/tutorials/services/connect-applications-service/#accessing-the-service)
            ```sh
            kubectl run curl --namespace=$K8S_NAMESPACE --image=radial/busyboxplus:curl -i --tty -- sh
            # use "exec" if curl pod already exists
            kubectl exec curl --namespace=$K8S_NAMESPACE -i --tty -- sh
            ```
        1. check endpoints
            ```sh
            [ root@curl:/ ]$ check_endpoint() {
                url=$1
                curl -s -o /dev/null "$url" && echo -e "[UP]\t${url}" || echo -e "[DOWN]\t${url}"
            }

            [ root@curl:/ ]$ check_farm_status() {
                echo "======================================================================"
                echo "Farm status:"
                echo "----------------------------------------------------------------------"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/agents/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/dashboard/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/jobs/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/jobs/load"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/logs/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/retries/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/tasks/status"
                check_endpoint "farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/tasks/list?status=submitted"
                echo "======================================================================"
            }

            [ root@curl:/ ]$ check_farm_status
            ```
    1. log into queue management dashboard
        http://farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/dashboard
        http://farm.23711a66dc7f46649e88.eastus.aksapp.io/queue/management/ui/
    1. Find api docs
        http://farm.23711a66dc7f46649e88.eastus.aksapp.io/docs
        * Issue Cannot find docs.
    1. Explore ConfigMaps


### 4. Submit job

1. Prerequisites
    * Python
    * Script dependancies
        ```
        pip install requests
        pip install toml
        ```
1. Download sample job
    download the example sample jobs: 
    ```
    ngc registry resource download-version "nvidia/omniverse-farm/cpu_verification:1.0.0"
    ngc registry resource download-version "nvidia/omniverse-farm/gpu_verification:1.0.0"
    ```
1. Get Jobs API Key
    ```sh
    kubectl get cm omniverse-farm-jobs -o yaml -n $K8S_NAMESPACE | grep api_key
    FARM_API_KEY=<api_key>
    ```
1. Upload job definitions to cluster
    ```sh
    FARM_BASE_URL="http://farm.23711a66dc7f46649e88.eastus.aksapp.io"
    python3 ./job_definition_upload.py df.kit   --farm-url=$FARM_BASE_URL --api-key=$FARM_API_KEY
    python3 ./job_definition_upload.py gpu.kit  --farm-url=$FARM_BASE_URL --api-key=$FARM_API_KEY
    ```
1. Get Job definitions
    ```sh
    curl -X 'GET' \
    "${FARM_BASE_URL}/agent/operator/job/definitions" \
    -H 'accept: application/json'
    ```
    * TODO: wrong endpoint. fix^
1. Submit CPU test job (df)
    ```sh
    curl -X "POST" \
    "${FARM_BASE_URL}/queue/management/tasks/submit" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "testuser",
    "task_type": "df",
    "task_args": {},
    "metadata": {
        "_retry": {
        "is_retryable": false
        }
    },
    "status": "submitted"
    }'
    ```
1. Submit GPU test job
    ```sh
    curl -X "POST" \
    "${FARM_BASE_URL}/queue/management/tasks/submit" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "user": "testuser",
    "task_type": "gpu",
    "task_args": {},
    "metadata": {
        "_retry": {
        "is_retryable": false
        }
    },
    "status": "submitted"
    }'
    ```

https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse-farm/resources/gpu_verification/quick-start-guide

## Troubleshooting 

### How to get current installed drivers?
### Are nvidia drivers pre-installed on NV series VMs?
### azurerm terrafrom provider support for enabling aks preview feature GPUDedicatedVHDPreview using terraform.

* pending [azurerm custom header support](https://github.com/hashicorp/terraform-provider-azurerm/issues/6793)
* [failed PR](https://github.com/hashicorp/terraform-provider-azurerm/pull/14178) tried to fix this.
* pending [AKS custom feature support](https://github.com/Azure/AKS/issues/2757)
* possible work around using [xpd provider](https://registry.terraform.io/providers/0x2b3bfa0/xpd/latest/docs/guides/test)

### ISSUE: Cannot find swagger docs at `/docs` after deploying helm chart to AKS

Helm chart does not seem to deploy a swagger docs. 

### ISSUE: kubectl not working on wsl2

fix is to copy over kube config
```
mkdir ~/.kube \ && cp /mnt/c/Users/nycjyp/.kube/config ~/.kube
```

## ref

* https://docs.omniverse.nvidia.com/app_farm/app_farm/omniverse_farm_cloud_setup.html
* https://github.com/NVIDIA/k8s-device-plugin#deployment-via-helm
* https://www.youtube.com/watch?v=KplFFvj3XRk
* https://itnext.io/enabling-nvidia-gpus-on-k3s-for-cuda-workloads-a11b96f967b0
* https://learn.microsoft.com/en-us/azure/aks/node-access - node access
* https://forums.developer.nvidia.com/t/set-up-cloud-rendering-using-aws-farm-queue/221879/3?u=mati-nvidia
* https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html
* https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
* https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/

### configure GPU nodes

* https://learn.microsoft.com/en-us/azure/aks/gpu-cluster#manually-install-the-nvidia-device-plugin
* https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/aks/gpu-cluster.md

### Setting up VMs

* https://azuremarketplace.microsoft.com/en-us/marketplace/apps/nvidia.ngc_azure_17_11?tab=overview
* https://michaelcollier.wordpress.com/2017/08/04/how-to-setup-nvidia-driver-on-nv-series-azure-vm/
