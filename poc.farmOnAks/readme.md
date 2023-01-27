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
        --node-vm-size Standard_NV6ads_A10_v5 \
        --node-taints sku=gpu:NoSchedule \
        --aks-custom-headers UseGPUDedicatedVHD=true \
        --enable-cluster-autoscaler \
        --min-count 1 \
        --max-count 3 \
        --os-sku Ubuntu \
        --mode User \
        --labels vm_type=GPU
    ```
1. [optionally] Update nodepool e.g. to add labels (expensive to recreate)
    ```
    az aks nodepool update \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool \
        --labels vm_type=GPU 
    ```
1. Verify that GPUs are schedulable
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
    ```
1. Get logs
    ```
    kubectl get pods --selector app=samples-tf-mnist-demo
    kubectl logs <pod_name>
    ````
1. Clean-up resources
    ```
    az aks nodepool delete \
        --resource-group dt-sandbox-resources \
        --cluster-name ovfarm-dev-aks-cluster \
        --name gpunodepool
    ```

### 2b. Deploy GPU Node Pool from Daemonset (Untested)

### 2c. Manually configure nodes the hard way (Don't do this)

#### Deploy Nvidia Device Plugin for K8s (via helm)

> TODO: Verifiy [Device Plugin prerequisites](https://github.com/NVIDIA/k8s-device-plugin#prerequisites):
> * NVIDIA drivers ~= 384.81
> * nvidia-docker >= 2.0 || nvidia-container-toolkit >= 1.7.0 (>= 1.11.0 to use integrated GPUs on Tegra-based systems)
> * nvidia-container-runtime configured as the default low-level runtime
> * Kubernetes version >= 1.10

1. Configure Device Plugin (to only run on GPU nodes)
    1. Create `containers/speckle/values.yaml`
        ```
        nodeSelector:
            vm_type: "GPU"
        ```
1. Install Containers
    1. connect to cluster
        ```
        az aks get-credentials \
            --resource-group "dt-sandbox-resources" \
            --name "ovfarm-dev-aks-cluster"
        ```
    1. install **helm chart** repo (one-time)
        ```
        helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
        helm repo update
        ```
    1. check avail repos
        ```
        helm repo list
        ```
    1. install device plugin
        ```
        helm upgrade -i nvdp nvdp/nvidia-device-plugin \
            --namespace nvidia-device-plugin \
            --create-namespace \
            --version 0.13.0 \ 
            --set nodeSelector.vm_type=GPU
        ```
        or
        ```
        helm install \
            --values ./nvidia-device-plugin/values.yaml \
            nvdp nvdp/nvidia-device-plugin \
            --namespace nvidia-device-plugin \
            --create-namespace \
            --version 0.13.0 
        ```
    1. check that chart has been released
        ```
        helm list --all-namespaces
        ```
    1. verify the number of GPUs
        ```
        kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
        ```
    1. [optionally] clean-up resources

#### Install NVIDIA driver (version 470.52.02) (Manually)

https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions

> TODO: find/create a custom VM image with this drivers, nvidia toolkit, etc. pre-installed, or create a script that automates setup.

1. ssh into a nodes
    1. Get Node ids
        ```
        kubectl get nodes -o wide
        ```
    1. ssh into nodes (from windows)
        ```sh
        # kubectl debug node/<node_id> -it --image=mcr.microsoft.com/dotnet/runtime-deps:6.0
        # for example:
        kubectl debug node/aks-nodepool-14001874-vmss000001 -it --image=mcr.microsoft.com/dotnet/runtime-deps:6.0
        ```
1. check drivers (according to https://github.com/Azure/aks-engine/blob/master/docs/topics/gpu.md nvidia drivers are pre-installed but need to verify.)
    1. get list
        ```
        dpkg --list | grep nvidia
        ```
    1. get details
        ```
        apt-cache show nvidia-*
        ```
1. check runtime env.
    1. get distro / architecture
        ```
        uname -a
        cat /etc/*-release
        dpkg --print-architecture
        ```
    1. get init
        ```
        apt-get update && apt-get install procps
        ps -p 1 -o comm=
        ```
1. download/install drivers from nvidia (470.161.03 - https://www.nvidia.com/Download/driverResults.aspx/194750/en-us/)
    1. install utils/deps
        ```
        apt update
        apt install pciutils
        apt-get install wget
        ```
    1. verify CUDA-capable GPU
        ```
        lspci | grep -i NVIDIA
        ```
    1. Download drivers
        CUDA_DRIVERS_PKG=cuda-drivers-510_510.47.03-1_amd64.deb \
        CUDA_REPO_PKG=cuda-11-6_11.6.2-1_amd64.deb \
        CUDA_RUNTIME_PKG=cuda-runtime-11-6_11.6.2-1_amd64.deb \
        CUDA_TOOLKIT_PKG=cuda-toolkit-11-6_11.6.2-1_amd64.deb \
        CUDA_DEMO_SUITE_PKG=cuda-demo-suite-11-6_11.6.55-1_amd64.deb
        CUDA_PKG=cuda-11-7_11.7.1-1_amd64.deb
        wget -O /tmp/${CUDA_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_PKG} 
        dpkg -i /tmp/${CUDA_PKG}

        wget -O /tmp/${CUDA_DRIVERS_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_DRIVERS_PKG} \
        wget -O /tmp/${CUDA_RUNTIME_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_RUNTIME_PKG} \
        wget -O /tmp/${CUDA_TOOLKIT_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_TOOLKIT_PKG} \
        wget -O /tmp/${CUDA_DEMO_SUITE_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_DEMO_SUITE_PKG} \
        wget -O /tmp/${CUDA_REPO_PKG} https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/${CUDA_REPO_PKG} 

        dpkg -i /tmp/${CUDA_DRIVERS_PKG} \
        dpkg -i /tmp/${CUDA_RUNTIME_PKG} \
        dpkg -i /tmp/${CUDA_TOOLKIT_PKG} \
        dpkg -i /tmp/${CUDA_DEMO_SUITE_PKG} \
        dpkg -i /tmp/${CUDA_REPO_PKG}

        -v525-

        LIBNV_COM=libnvidia-common-525_525.60.13-0ubuntu1_all.deb \

        LIBX=libx11-6_1.8.1-2_amd64.deb \
        LIBXEXT=libxext6_1.3.4-1+b1_amd64.deb \
        LIBNV_COMPUTE=libnvidia-compute-525_525.60.13-0ubuntu1_amd64.deb \

        LIBNV_DECODE=libnvidia-decode-525_525.60.13-0ubuntu1_amd64.deb \
        LIBNV_ENCODE=libnvidia-encode-525_525.60.13-0ubuntu1_amd64.deb \
        LIBNV_FBC1=libnvidia-fbc1-525_525.60.13-0ubuntu1_amd64.deb \
        LIBNV_GL=libnvidia-gl-525_525.60.13-0ubuntu1_amd64.deb \
        NV_COMPUTE_UTILS=nvidia-compute-utils-525_525.60.13-0ubuntu1_amd64.deb \
        NV_DKMS=nvidia-dkms-525_525.60.13-0ubuntu1_amd64.deb \
        NV_DRIVER=nvidia-driver-525_525.60.13-0ubuntu1_amd64.deb \
        NV_KERNAL_COM=nvidia-kernel-common-525_525.60.13-0ubuntu1_amd64.deb \
        NV_KERNAL_SOURCE=nvidia-kernel-source-525_525.60.13-0ubuntu1_amd64.deb \
        NV_DRIVERS=cuda-drivers-525_525.60.13-1_amd64.deb

        wget -O /tmp/${LIBNV_COM} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_COM} \
        wget -O /tmp/${LIBX} http://ftp.ca.debian.org/debian/pool/main/libx/libx11/${LIBX} \
        wget -O /tmp/${LIBXEXT} http://ftp.ca.debian.org/debian/pool/main/libx/libx11/${LIBXEXT} \
        wget -O /tmp/${LIBNV_COMPUTE} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_COMPUTE} \
        wget -O /tmp/${LIBNV_DECODE} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_DECODE} \
        wget -O /tmp/${LIBNV_ENCODE} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_ENCODE} \
        wget -O /tmp/${LIBNV_FBC1} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_FBC1} \
        wget -O /tmp/${LIBNV_GL} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${LIBNV_GL} \
        wget -O /tmp/${NV_COMPUTE_UTILS} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_COMPUTE_UTILS} \
        wget -O /tmp/${NV_DKMS} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_DKMS} \
        wget -O /tmp/${NV_DRIVER} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_DRIVER} \
        wget -O /tmp/${NV_KERNAL_COM} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_KERNAL_COM} \
        wget -O /tmp/${NV_KERNAL_SOURCE} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_KERNAL_SOURCE} \
        wget -O /tmp/${NV_DRIVERS} https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/${NV_DRIVERS} 

        dpkg -i /tmp/${LIBNV_COM} \
        dpkg -i /tmp/${LIBX} \
        dpkg -i /tmp/${LIBXEXT} \
        dpkg -i /tmp/${LIBNV_COMPUTE} \
        dpkg -i /tmp/${LIBNV_DECODE} \
        dpkg -i /tmp/${LIBNV_ENCODE} \
        dpkg -i /tmp/${LIBNV_FBC1} \
        dpkg -i /tmp/${LIBNV_GL} \
        dpkg -i /tmp/${NV_COMPUTE_UTILS} \
        dpkg -i /tmp/${NV_DKMS} \
        dpkg -i /tmp/${NV_DRIVER} \
        dpkg -i /tmp/${NV_KERNAL_COM} \
        dpkg -i /tmp/${NV_KERNAL_SOURCE} \
        dpkg -i /tmp/${NV_DRIVERS}

        apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/3bf863cc.pub

        rm -f /tmp/${CUDA_DRIVERS_PKG}
        rm -f /tmp/${CUDA_RUNTIME_PKG}
        rm -f /tmp/${CUDA_TOOLKIT_PKG}
        rm -f /tmp/${CUDA_DEMO_SUITE_PKG}
        rm -f /tmp/${CUDA_REPO_PKG}

        GLX_ALT=glx-alternative-nvidia_1.2.1_amd64.deb
        wget -O /tmp/${GLX_ALT} http://ftp.ca.debian.org/debian/pool/contrib/g/glx-alternatives/${GLX_ALT}
        dpkg -i /tmp/${GLX_ALT}

        apt-get update
        apt-get install cuda-drivers

        https://learn.microsoft.com/en-us/azure/virtual-machines/linux/n-series-driver-setup

    1. fix systemctl
        find / -name systemctl 2>/dev/null
        export PATH=$PATH:/host/bin
        echo $LD_LIBRARY_PATH
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/host/lib/systemd
        export XXX=$LD_LIBRARY_PATH:/host/lib/x86_64-linux-gnu
        libcap.so.2
        libip4tc.so.0
        libsystemd-shared-237.so


#### Install NVIDIA Container Toolkit (via containerd)

> TODO: Verify Container Toolkit prerequisites:
> * GNU/Linux x86_64 with kernel version > 3.10
> * Docker >= 19.03 (recommended, but some distributions may include older versions of Docker. The minimum supported version is 1.12)
> * NVIDIA GPU with Architecture >= Kepler (or compute capability 3.0)
> * NVIDIA Linux drivers >= 418.81.07 (Note that older driver releases or branches are unsupported.)

> TODO: find/create a custom VM image with this drivers, nvidia toolkit, etc. pre-installed, or create a script that automates setup.

> ISSUE: restart containerd failing in final step b/c NO SYSTEMCTL!!!:( 

1. install containerd
    1. install dependancies
        ```
        apt-get update
        apt-get install \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        ```
    1. Add the repository GPG key and the repo:
        ```
        curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        ```
        might have to do this instead:
        ```
        curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
        ```
    1. verify ___
        don't do this:
        ```
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        (lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        ```
        do this instead:
        ```
        echo "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" | tee /etc/apt/sources.list.d/docker.list
        ```
    1. Install containerd
        ```
        apt-get update && apt-get install -y containerd.io
        ```
    1. configure containerd w/ default config
        ```
        mkdir -p /etc/containerd \
            && containerd config default | tee /etc/containerd/config.toml
        ```
    1. configure containerd for nvidia container runtime (apply patch)
        ```
        cat <<EOF > containerd-config.patch
        --- config.toml.orig    2020-12-18 18:21:41.884984894 +0000
        +++ /etc/containerd/config.toml 2020-12-18 18:23:38.137796223 +0000
        @@ -94,6 +94,15 @@
                privileged_without_host_devices = false
                base_runtime_spec = ""
                [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
        +            SystemdCgroup = true
        +       [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
        +          privileged_without_host_devices = false
        +          runtime_engine = ""
        +          runtime_root = ""
        +          runtime_type = "io.containerd.runc.v1"
        +          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
        +            BinaryName = "/usr/bin/nvidia-container-runtime"
        +            SystemdCgroup = true
            [plugins."io.containerd.grpc.v1.cri".cni]
            bin_dir = "/opt/cni/bin"
            conf_dir = "/etc/cni/net.d"
        EOF
        ```
    1. restart containerd:
        ```
        systemctl restart containerd
        ```

ref:
* https://docs.omniverse.nvidia.com/app_farm/app_farm/omniverse_farm_cloud_setup.html#deploying-the-helm-chart
* https://unix.stackexchange.com/questions/626645/how-to-install-containerd-on-debian


1. Install Nvidia Container Toolkit
    1. xxx
        ```
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
            && curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | apt-key add - \
            && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        ```
    1. Install Nvidia Container Toolkit
        ```
        sudo apt-get update \
            && sudo apt-get install -y nvidia-container-toolkit
        ```

--- test 1  -----------------------------

ctr image pull docker.io/library/hello-world:latest 
ctr run --rm -t docker.io/library/hello-world:latest hello-world

https://learn.microsoft.com/en-us/azure/aks/node-access - node access

--- test2 a GPU container -----------------------

ctr image pull docker.io/nvidia/cuda:11.6.2-base-ubuntu20.04

ctr run --rm -t \
    --runc-binary=/usr/bin/nvidia-container-runtime \
    --env NVIDIA_VISIBLE_DEVICES=all \
    docker.io/nvidia/cuda:11.6.2-base-ubuntu20.04 \
    cuda-11.6.2-base-ubuntu20.04 nvidia-smi

--- test 3 from https://itnext.io/enabling-nvidia-gpus-on-k3s-for-cuda-workloads-a11b96f967b0

ctr image pull docker.io/nvidia/cuda:11.0-base
ctr run --rm --gpus 0 -t docker.io/nvidia/cuda:11.0-base cuda-11.0-base nvidia-smi

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
    NAMESPACE="ovfarm"
    NGC_API_KEY=<NGC_API_TOKEN>
1. Create namespace
    ```
    kubectl create namespace $NAMESPACE
    ```
    * Question: can this be default namespace?
1. Create [Docker Config Secret](https://kubernetes.io/docs/concepts/configuration/secret/#docker-config-secrets)
    ```
    kubectl create secret docker-registry my-registry-secret \
        --namespace $NAMESPACE \
        --docker-server="nvcr.io" \
        --docker-username='$oauthtoken' \
        --docker-password=$NGC_API_TOKEN
    ```
1. fetch helm chart
    ```
    helm fetch https://helm.ngc.nvidia.com/nvidia/omniverse/charts/omniverse-farm-0.3.2.tgz \
        --username='$oauthtoken' \
        --password=$NGC_API_TOKEN
    ```
1. install farm
    ```
    helm upgrade \
        --install \
            omniverse-farm \
            omniverse-farm-0.3.2.tgz \
        --create-namespace \
        --namespace $NAMESPACE \
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
        kubectl get pods -o wide
        ```
    1. Ensure all pods in ready state
        ```sh
        kubectl -n $NAMESPACE wait --timeout=300s --for condition=Ready pods --all
        
        ```
        * Note, controller takes a very long time to initialize
    1. Check for errors for any pod that aren't ready
        ```sh
        kubectl describe pod <pod_name>
        ```
    1. Try endpoints!
        ```
        https://saz-dev.eastus.cloudapp.azure.com/
        https://saz-dev.eastus.cloudapp.azure.com/graphql
        ```
    1. Check endpoints with curl pod
        1. [run curl pod](https://kubernetes.io/docs/tutorials/services/connect-applications-service/#accessing-the-service)
            ```sh
            kubectl run curl --namespace=$NAMESPACE --image=radial/busyboxplus:curl -i --tty -- sh
            # use "exec" if curl pod already exists
            kubectl exec curl --namespace=$NAMESPACE -i --tty -- sh
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
    ```
    download the example df.kit job and sample upload script:
    ```
1. Get Jobs API Key
    ```
    kubectl get cm omniverse-farm-jobs -o yaml -n $NAMESPACE | grep api_key
    FARM_API_KEY=<api_key>
    ```
1. Upload job definition to cluster
    ```
    FARM_BASE_URL="http://farm.23711a66dc7f46649e88.eastus.aksapp.io/"
    python3 ./job_definition_upload.py df.kit --farm-url=$FARM_BASE_URL --api-key=$FARM_API_KEY
    ```
1. Get Job definitions
    ```
    curl -X 'GET' \
    "${FARM_BASE_URL}/agent/operator/job/definitions" \
    -H 'accept: application/json'
    ```
1. Submit job 
    ```
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

### 5. Submit GPU test job

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
