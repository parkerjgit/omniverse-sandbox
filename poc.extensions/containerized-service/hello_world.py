from omni.services.core import main

def hello_world():
  return "hello containerized service"
  
main.register_endpoint("get", "/hello-world", hello_world)