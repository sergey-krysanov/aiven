import threading
import time
import json
from kafka import KafkaConsumer, TopicPartition
from common.config import get_config
from common.logger import get_logger
logger = get_logger('consumer')
from common.db_model import DbModel

CONSUMER_JOBS_COUNT = 2
CONSUMER_MAX_RECORDS = 100


class ConsumerJob(object):
    def __init__(self, config):
        self.config = config
        kafka = config['kafka']
        self.consumer = None
        self.partition = TopicPartition(kafka['TOPIC'], 0)
        self.stopping = threading.Event()
        self.thread = None

    def create_consumer(self):
        kafka = self.config['kafka']
        assert self.consumer is None
        self.consumer = KafkaConsumer(
            bootstrap_servers=kafka['SERVICE_URI'],
            security_protocol="SSL",
            ssl_cafile=kafka['CA_PATH'],
            ssl_certfile=kafka['CERT_PATH'],
            ssl_keyfile=kafka['KEY_PATH'],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            client_id=kafka['client_id'],
            group_id=kafka['group_id'],
        )
        self.consumer.assign([self.partition])

    def start(self):
        assert self.thread is None
        self.stopping.clear()
        self.create_consumer()
        self.thread = threading.Thread(target=self.execute)
        self.thread.start()

    def stop(self):
        self.stopping.set()
        self.thread.join()
        self.thread = None
        self.consumer.close()
        self.consumer = None

    def execute(self):
        db_model = DbModel(self.config)
        while not self.stopping.isSet():
            try:
                offset = self.consumer.position(self.partition)
                msg_pack = self.consumer.poll(timeout_ms=1000,
                    max_records=CONSUMER_MAX_RECORDS)
                messages = msg_pack.get(self.partition, [])
                values = [json.loads(m.value.decode('utf-8'))
                          for m in messages]
                db_model.save_metrics(values)
                self.consumer.commit()
            except Exception as ex:
                logger.exception(ex)
                self.consumer.seek(self.partition, offset)
            self.stopping.wait(0)


def run_consumer():
    config = get_config()
    jobs = []
    for i in range(CONSUMER_JOBS_COUNT):
        job = ConsumerJob(config)
        job.start()
        jobs.append(job)

    try:
        while True:
            try:
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                logger.info("Stopping service")
                break
    finally:
        for job in jobs:
            job.stop()
    logger.info("Service is stopped")
