import omni.ext
from omni.services.core import main

def hello_world():
    return "hello super simple service!!"

class PocServicesSimpleExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        main.register_endpoint("get", "/hello-world", hello_world)

    def on_shutdown(self):
        main.deregister_endpoint("get", "/hello-world")
