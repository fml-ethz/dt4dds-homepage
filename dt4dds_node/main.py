import logging
import time
import pathlib
import signal
import sys

import connector
import worker

BASE_PATH = pathlib.Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s][%(asctime)s][%(name)s][%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(pathlib.Path(BASE_PATH / 'files' / 'logs' / 'node.log', mode='a')), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


LOOP_DELAY_IDLE = 1
LOOP_DELAY_RUNNING = 1
ROOT_DIR = pathlib.Path(BASE_PATH / 'files' / 'jobs')

logger.info("Starting up")

# initialize communication and processing
dispatch = connector.Connector()
factory = worker.Worker()


# set up termination handling
def signal_handler(*args):  
    logger.warning("Received signal, shutting down")
    factory.kill_process()
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler) 
signal.signal(signal.SIGTERM, signal_handler)


# test connection
conn_exists = dispatch.notify_start() == 'ACK'
while not conn_exists:
    logger.error("Connection could not be established, waiting ...")
    time.sleep(5)
    conn_exists = dispatch.notify_start() == 'ACK'
logger.info("Connection established, continuing ...")

# main loop
while True:

    if factory.state == factory.States.IDLE:

        data = dispatch.query_job()

        if data and 'uid' in data:
            logger.info(f"Starting job {data['uid']}")
            working_dir = ROOT_DIR / str(data['uid'])
            factory.start_process(working_dir, data['uid'])
            dispatch.notify_job_start(data['uid'])

        else:
            time.sleep(LOOP_DELAY_IDLE)


    elif factory.state == factory.States.WORKING:
        
        if factory.process_alive():
            if factory.constraints_violated():
                logger.warning(f"Job {data['uid']} violated constraints, killing")
                dispatch.notify_job_fail(factory.current_uid)
                factory.kill_process()
                factory.clear()

        else:
            if factory.job_successful():
                dispatch.notify_job_finish(factory.current_uid)
                logger.info(f"Job {data['uid']} finished")
            else:
                dispatch.notify_job_fail(factory.current_uid)
                logger.error(f"Job {data['uid']} failed")
            
            factory.clear()

        time.sleep(LOOP_DELAY_RUNNING)
