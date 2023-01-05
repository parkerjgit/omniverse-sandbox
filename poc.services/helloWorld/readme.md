# Minimal Service

## Prerequisites

1. Kit installed and location of `kit.exe` is added to path, e.g. `C:\Users\nycjyp\AppData\Local\ov\pkg\kit-104.1.0`

## Setup

1. create a python function to handle request and register it with an endpoint:
    ```py
    from omni.services.core import main

    def hello_world():
        return "hello world"
    
    main.register_endpoint("get", "/hello-world", hello_world)
    ```
2. start service with kit
    ```
    kit \
      --exec hello_world.py \
      --enable omni.services.core \
      --enable omni.services.transport.server.http \
      --/exts/omni.kit.registry.nucleus/registries/0/name=kit/services \
      --/exts/omni.kit.registry.nucleus/registries/0/url=https://dw290v42wisod.cloudfront.net/exts/kit/services
    ```
1. Inspect log - Should see "app ready" after all dependancies resolved are started up.
1. Navigate to OpenAPI docs at `http://localhost:8011/docs` which include `/hello-world` endpoint.
1. Test endpoint:
    ```
    curl -X 'GET' \
        'http://localhost:8011/hello-world' \
        -H 'accept: application/json'
    ```

## Ref

* [Omniverse Services Getting Started](https://docs.omniverse.nvidia.com/prod_services/prod_services/design/getting_started.html)
