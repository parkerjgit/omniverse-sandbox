import omni.ext
from omni.services.core import main

def hello_headless():
    return "hello headless service!!"

class PocServicesHeadlessExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        main.register_endpoint("get", "/hello_headless", hello_headless)

    def on_shutdown(self):
        main.deregister_endpoint("get", "/hello_headless")
