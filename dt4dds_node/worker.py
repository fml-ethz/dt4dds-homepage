import enum
import time
import subprocess

import logging
logger = logging.getLogger(__name__)

TIME_LIMIT = 15*60


class Worker():

    class States(enum.Enum):
        IDLE = 1
        WORKING = 2


    state = States.IDLE

    process = None
    start_time = None
    current_dir = None
    current_uid = None


    def start_process(self, working_dir, uid):
        self.process = subprocess.Popen(
            ['python3', 'dt4dds_node/runner.py', working_dir]
        )

        self.state = self.States.WORKING
        self.start_time = time.time()
        self.current_dir = working_dir
        self.current_uid = uid


    def process_alive(self):
        if self.state == self.States.IDLE:
            return False
        elif self.process == None:
            return False
        else:
            return self.process.poll() == None
        

    def job_successful(self):
        if self.process:
            self.process.poll()
            logger.info(f"Job finished with return code {self.process.returncode}.")
            return self.process.returncode == 0
        else:
            return False

    
    def constraints_violated(self):
        if self.state == self.States.IDLE:
            return False
        elif self.process == None:
            return False
        else:
            return (time.time()-self.start_time) > TIME_LIMIT


    def kill_process(self):
        if self.process:
            self.process.kill()


    def clear(self):
        self.state = self.States.IDLE
        self.process = None
        self.start_time = None
        self.current_dir = None
        self.current_uid = None


