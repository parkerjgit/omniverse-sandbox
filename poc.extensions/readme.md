# Creating microservice extensions

## Minimal Service

1. Prerequisites:
    * Kit installed and added to path.
1. Register request handler with an endpoint:
    ```py
    from omni.services.core import main

    def hello_world():
        return "hello world"
    
    main.register_endpoint("get", "/hello-world", hello_world)
    ```
1. Start service with `kit.exe` by passing config.
    ```
    kit \
      --exec hello_world.py \
      --enable omni.services.core \
      --enable omni.services.transport.server.http \
      --/exts/omni.kit.registry.nucleus/registries/0/name=kit/services \
      --/exts/omni.kit.registry.nucleus/registries/0/url=https://dw290v42wisod.cloudfront.net/exts/kit/services
    ```
    > Note, should see "app ready" logged after all dependancies are resolved and started up.
1. Navigate to OpenAPI docs at `http://localhost:8011/docs` which now includes `/hello-world` endpoint.
1. Test endpoint:
    ```
    curl -X 'GET' \
        'http://localhost:8011/hello-world' \
        -H 'accept: application/json'
    ```

## Simple Service (linked to app)

1. Generate "New Extension Template Project" scaffolding, from Omniverse Code Extensions tab, by clicking "+" icon.
    * **name** - repo root directory, can be anything, e.g. "simple-service"
    * **id** - python module (namespace), e.g. "poc.services.simple"
1. [If nec.] [Link with Omniverse app](https://github.com/NVIDIA-Omniverse/kit-extension-template#linking-with-an-omniverse-app)
    ```
    link_app.sh --app kit
    ```
1. Verify that python module is correctly specified in [config/extension.toml](./simple-service/exts/poc.services.simple/config/extension.toml) file:
    ```toml
    # available as "import poc.services.simple"
    [[python.module]]
    name = "poc.services.simple"
    ```
1. Add `omni.services.core` to dependancies in [config/extension.toml](./simple-service/exts/poc.services.simple/config/extension.toml) file:
    ```toml
    [dependencies]
    "omni.services.core" = {}
    ```
1. Implement `on_startup` and `on_shutdown` methods to register/deregister handler with endpoint (in [extension.py](./simple-service/exts/poc.services.simple/poc/services/simple/extension.py) file):
    ```py
    import omni.ext
    from omni.services.core import main

    def hello_world():
        return "hello world"

    class PocServicesSimpleExtension(omni.ext.IExt):

        def on_startup(self, ext_id):
            main.register_endpoint("get", "/hello-world", hello_world)

        def on_shutdown(self):
            main.deregister_endpoint("get", "/hello-world")
    ```
1. Launch Omniverse Code with `poc.services.simple` extension enabled
    ```
    app\omni.code.bat ^
        --ext-folder ./exts ^
        --enable poc.services.simple
    ```
1. Navigate to OpenAPI docs at `http://localhost:8211/docs` which include `/hello-world` endpoint.
1. Test endpoint:
    ```
    curl -X 'GET' \
        'http://localhost:8011/hello-world' \
        -H 'accept: application/json'
    ```

## Headless service

1. Prerequisites
    * Kit installed and added to path
1. Clone [Omniverse Kit Extensions Project Template](https://github.com/NVIDIA-Omniverse/kit-extension-template) into project root
    ```
    git clone git@github.com:NVIDIA-Omniverse/kit-extension-template.git .
    ```
1. Start service by passing configuration to `kit.exe`
    ```
    app/kit.exe \
        --ext-folder ./exts \
        --enable poc.services.headless \
        --enable omni.services.transport.server.http \
        --/exts/omni.kit.registry.nucleus/registries/0/name=kit/services \
        --/exts/omni.kit.registry.nucleus/registries/0/url=https://dw290v42wisod.cloudfront.net/exts/kit/services
    ```
    > Note Omniverse services extensions do not ship with kit, which is why we are passing in registery name and address, where they can be downloaded from.
    > While we can launch extension headlessly this way, if we *really* want to run headlessly, we should [create an app](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/104.0/guide/creating_kit_apps.html#building-an-app) (ie., an entry point). Recall, that an app is just a `.kit` file.
1. Create App, ie., a `.kit` file:
    ```toml
    [settings.app.exts.folders]
    '++' = ["./exts"]

    [settings.exts]
    "omni.services.transport.server.http".port = 8311
    "omni.kit.registry.nucleus".registries = [
    { name = "kit/services", url = "https://dw290v42wisod.cloudfront.net/exts/kit/services"},
    ]

    [dependencies]
    "omni.services.transport.server.http" = {}
    "poc.services.headless" = {}
    ```
1. Start service
    ```
    kit headless-service.kit
    ```

## Containerized Service

1. [If nec.] Generate API Key [here](https://ngc.nvidia.com/setup/api-key)
1. Login to nvcr.io using API Key and username '$oauthtoken'
    ```
    docker login nvcr.io
    ```
1. Create a [dockerfile](./containerized-service/dockerfile) that adds [hello_world.py](./containerized-service/hello_world.py) to [KIT SDK base image](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/containers/kit)
    ```dockerfile
    # Start with Kit Base image
    FROM nvcr.io/nvidia/omniverse/kit:103.5.1

    # Install services dependencies on image (omni.services does not ship with Kit)
    # This code is pulled from a extension registry and the --ext-precache-mode will pull down the extensions and exit.
    RUN /opt/nvidia/omniverse/kit-sdk-launcher/kit \
        --ext-precache-mode \
        --enable omni.services.core \
        --enable omni.services.transport.server.http \
        --/exts/omni.kit.registry.nucleus/registries/0/name=kit/services \
        --/exts/omni.kit.registry.nucleus/registries/0/url=https://dw290v42wisod.cloudfront.net/exts/kit/services \
        --allow-root

    # Add script to image
    COPY hello_world.py /hello_world.py

    # Declare *intention* for container to use port 8011 at runtime
    EXPOSE 8011/tcp

    # Configure container as an executable
    ENTRYPOINT [ \
        "/opt/nvidia/omniverse/kit-sdk-launcher/kit", \
        "--exec", "hello_world.py", \
        "--enable omni.services.core", \ 
        "--enable", "omni.services.transport.server.http", \
        "--allow-root"]
    ```
1. Build a new image from dockerfile named "hello-world"
    ```sh
    docker build -t hello-world .
    docker images hello-world
    ```
1. Create a new executable container from latest hello-world image and run it locally on port 8011.
    ```
    docker run -it -p 8011:8011 hello-world:latest
    ```
1. Navigate to OpenAPI docs at `http://localhost:8011/docs` which now include `/hello-world` endpoint.
1. Test endpoint:
    ```
    curl -X 'GET' \
        'http://localhost:8011/hello-world' \
        -H 'accept: application/json'
    ```

## Deploy Containerized App to ACI

1. Host in container registry
    1. [if nec] Create an Azure Container Registry (ACR)
        ```sh
        # az acr create --resource-group <resource-group> --name <acrName> --sku Basic
        az acr create --resource-group dt-sandbox-resources --name ovfarmacr --sku Basic --admin-enabled true
        ```
    1. Log in to container registry
        ```sh
        # az acr login --name <acrName>
        az acr login --name ovfarmacr
        ```
    1. Tag image
        ```sh
        # get full name of ACR instance (e.g., ovfarmacr.azurecr.io)
        az acr show --name ovfarmacr --query loginServer --output table

        # docker tag <source_image>:<tag> <acr_name>.azurecr.io/<target_image>:<tag>
        docker tag hello-world:latest ovfarmacr.azurecr.io/hello-world:latest
        ```
    1. Push image to container registry
        ```sh
        docker push ovfarmacr.azurecr.io/hello-world:latest

        # verify image is now stored in registry
        az acr repository show --name ovfarmacr --repository hello-world
        az acr repository list --name ovfarmacr --output table
        az acr repository show-tags --name ovfarmacr --repository hello-world --output table
        ```
1. Deploy App (using az container create)
    1. Get ACR credentials
        ```
        az acr credential show -g dt-sandbox-resources -n ovfarmacr
        ```
    1. Create Container Group
        ```
        ACR_PASSWORD=<acr_password>
        az container create \
            --resource-group dt-sandbox-resources \
            --name ov-demo-microservice \
            --image ovfarmacr.azurecr.io/hello-world:latest \
            --registry-login-server ovfarmacr.azurecr.io \
            --registry-username ovfarmacr \
            --registry-password $ACR_PASSWORD \
            --ip-address Public \
            --dns-name-label ov-demo-microservice \
            --ports 8011
        ```
    1. test endpoints
        ```
        http://ov-demo-microservice.eastus.azurecontainer.io:8011/docs
        http://ov-demo-microservice.eastus.azurecontainer.io:8011/hello-world
        http://ov-demo-microservice.eastus.azurecontainer.io:8011/status
        ```

## Ref

* [Omniverse Services Getting Started](https://docs.omniverse.nvidia.com/prod_services/prod_services/design/getting_started.html)
* [Omniverse microservice tutorials, 1](http://localhost:8211/tutorials/docs/source/extensions/omni.services.tutorials.one/docs/README.html)
* [Omniverse microservice tutorials, 2](http://localhost:8211/tutorials/docs/source/extensions/omni.services.tutorials.two/docs/README.html)
* [Omniverse Kit Extensions Project Template](https://github.com/NVIDIA-Omniverse/kit-extension-template)
* [Companion Code to A Deep Dive into Building Microservices with Omniverse](https://github.com/NVIDIA-Omniverse/deep-dive-into-microservices)
