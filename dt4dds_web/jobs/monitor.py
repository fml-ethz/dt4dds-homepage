import threading
from multiprocessing.connection import Listener
from django.utils import timezone
import pathlib

import logging
logger = logging.getLogger('dt4dds_web.jobs.monitor')
logger.setLevel(logging.INFO)

from .models import Job


class MonitorThread(threading.Thread):

    daemon = True

    address = ('localhost', 6003) 
    password = b'default'
    listener = None

    def run(self):
        
        try:
            self.listener = Listener(self.address, authkey=self.password)
            logger.info(f"Monitor started listening on {self.address}")
        except Exception as e:
            logger.error(f"Monitor could not start: {e}")
            return

        while True:
            conn = self.listener.accept()
            logger.debug(f'connection accepted from {self.listener.last_accepted}')

            msg = conn.recv()
            logger.debug(f'message received: {msg}')

            try:
                answer = self.handle_message(msg)
                if answer:
                    conn.send(answer)
                else:
                    conn.send(None)
            except Exception as e:
                logger.exception(e)
            finally:
                conn.close()


    def __del__(self):
        if self.listener:
            self.listener.close()


    def clear_running_jobs(self):
        # if there were jobs in running state, mark them as failed
        query = Job.objects.all().filter(state=Job.StateTypes.RUNNING).exclude(is_deleted=True)
        logger.debug(f"Total of {query.count()} running jobs are pending.")
        if query.count():
            for job in query:
                logger.warning(f"Failing job {job.uid} due to clear operation.")
                job.state = job.StateTypes.FAILED
                job.save()


    def handle_message(self, msg):

        cmd = msg['cmd']

        if cmd == "start":
            logger.info("New processing node connected.")
            self.clear_running_jobs()
            
            return 'ACK'


        elif cmd == "get_job":
            logger.debug("Processing node looks for work.")
            self.clear_running_jobs()

            query = Job.objects.all().filter(state=Job.StateTypes.WAITING).exclude(is_deleted=True)
            logger.debug(f"Total of {query.count()} jobs are waiting.")

            if query.count():
                job = query.earliest('submission_date')
                logger.info(f"Submitting job {job.uid}.")
                return {'uid': job.uid}

            else:
                # no answer necessary
                return


        elif cmd == "start_job":
            uid = msg['uid']
            job = Job.objects.get(pk=uid)
            logger.info(f"Processing node started working on job {job.uid}.")
            self.clear_running_jobs()

            job.state = job.StateTypes.RUNNING
            job.run_start_date = timezone.now()
            job.save()

            # no answer necessary
            return


        elif cmd == "finish_job":
            uid = msg['uid']
            job = Job.objects.get(pk=uid)
            logger.info(f"Processing node finished job {job.uid}.")

            if job.output_file.is_file():
                job.state = job.StateTypes.FINISHED
            else:
                logger.warning(f"Processing node reported success for job {job.uid}, but no output file found")
                job.state = job.StateTypes.FAILED
            job.run_end_date = timezone.now()
            job.save()

            # no answer necessary
            return


        elif cmd == "fail_job":
            uid = msg['uid']
            job = Job.objects.get(pk=uid)
            logger.warning(f"Processing node failed on job {job.uid}.")

            job.state = job.StateTypes.FAILED
            job.save()

            # no answer necessary
            return


        else:
            logger.error(f"Received unknown command: {cmd}")
            return
            



_INSTANCE = None

def start():
    global _INSTANCE
    if _INSTANCE == None:
        _INSTANCE = MonitorThread().start()
    return _INSTANCE


def stop():
    global _INSTANCE
    logger.error("Stopping monitor thread")
    if _INSTANCE != None:
        _INSTANCE.setDaemon(True)  
        _INSTANCE.__del__()
