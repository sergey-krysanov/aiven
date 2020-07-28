import json
from kafka import KafkaConsumer, TopicPartition
from common.config import get_config
from common.logger import get_logger
from common.db_model import DbModel

CONSUMER_MAX_RECORDS = 100

logger = get_logger('consumer')


def run_consumer():
    config = get_config()
    kafka = config['kafka']
    assert kafka['partition'] is not None
    partition = TopicPartition(kafka['topic'], int(kafka['partition']))
    consumer = KafkaConsumer(
        bootstrap_servers=kafka['service_uri'],
        security_protocol="SSL",
        ssl_cafile=kafka['ca_path'],
        ssl_certfile=kafka['cert_path'],
        ssl_keyfile=kafka['key_path'],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        client_id=kafka['client_id'],
        group_id=kafka['group_id'],
    )
    consumer.assign([partition])

    db_model = DbModel(config)

    logger.info("Start processing {topic}:{partition}"
                .format(topic=kafka['topic'], partition=kafka['partition']))

    while True:
        offset = None
        try:
            offset = consumer.position(partition)
            msg_pack = consumer.poll(timeout_ms=1000,
                                     max_records=CONSUMER_MAX_RECORDS)
            messages = msg_pack.get(partition, [])
            values = [json.loads(m.value.decode('utf-8'))
                      for m in messages]
            logger.debug("processing data: {}".format(values))
            db_model.save_metrics(values)
            consumer.commit()
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as ex:
            logger.exception(ex)
            if offset is not None:
                consumer.seek(partition, offset)

    logger.info("Service is stopped")
