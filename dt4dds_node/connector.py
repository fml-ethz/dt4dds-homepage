from multiprocessing.connection import Client

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class Connector():

    address = ('localhost', 6003)
    password = b'default' 
    listener = None


    def _connect(self):
        return Client(self.address, authkey=self.password)


    def _send_and_receive(self, msg):
        try:
            conn = self._connect()
            conn.send(msg)
            ans = conn.recv()
            conn.close()
        except EOFError:
            logger.error("Connection aborted")
            ans = None
        except ConnectionRefusedError:
            logger.error("Connection refused")
            ans = None            

        # return what was received
        return ans


    def notify_start(self):
        logger.info("Notifying connection for start ...")
        return self._send_and_receive({'cmd': 'start'})


    def query_job(self):
        logger.debug("Querying connection for job ...")
        return self._send_and_receive({'cmd': 'get_job'})

    
    def notify_job_start(self, job_id):
        logger.info(f"Notifying job start for id {job_id}.")
        return self._send_and_receive({'cmd': 'start_job', 'uid': job_id})


    def notify_job_finish(self, job_id):
        logger.info(f"Notifying job finished for id {job_id}.")
        return self._send_and_receive({'cmd': 'finish_job', 'uid': job_id})


    def notify_job_fail(self, job_id):
        logger.info(f"Notifying job failed for id {job_id}.")
        return self._send_and_receive({'cmd': 'fail_job', 'uid': job_id})
