import signal
from django.apps import AppConfig

class JobsConfig(AppConfig):
    name = 'jobs'

    def ready(self):
        from . import monitor
        monitor.start()


def monitor_handler(*args):  
    from . import monitor
    monitor.stop()
    
signal.signal(signal.SIGINT, monitor_handler) 
signal.signal(signal.SIGTERM, monitor_handler)