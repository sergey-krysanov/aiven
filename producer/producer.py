import time
import json
from kafka import KafkaProducer
from common.config import get_config
from common.logger import get_logger
from common.db_model import DbModel
from .site_checker import SiteChecker

logger = get_logger('producer')


def check_sites_availability(config, sites):
    kafka = config['kafka']
    producer = KafkaProducer(
        bootstrap_servers=kafka['service_uri'],
        security_protocol="SSL",
        ssl_cafile=kafka['ca_path'],
        ssl_certfile=kafka['cert_path'],
        ssl_keyfile=kafka['key_path'],
    )

    def on_url_check_completed_cb(site_id,
                                  status_code,
                                  response_time,
                                  failed_regexps):
        data = {
            'site_id': site_id,
            'status_code': status_code,
            'response_time_ms': response_time,
            'ts': time.time(),
            'failed_regexps': failed_regexps
        }
        logger.debug("Send metrics for site_id: {}".format(site_id))
        producer.send(kafka['topic'], json.dumps(data).encode("utf-8"))
        producer.flush()

    checkers = []
    for site in sites:
        checker = SiteChecker(site, config['check_interval'])
        checker.start(on_url_check_completed_cb)
        checkers.append(checker)

    try:
        while True:
            try:
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                logger.info("Stopping producer service")
                break
    finally:
        for checker in checkers:
            checker.stop()


def run_producer():
    logger.info('Starting producer service')
    config = get_config()
    try:
        db_model = DbModel(config)
        with db_model:
            sites = db_model.get_sites_list(config['group_name'])
        logger.info('Start checking sites: {}'.format([x[1] for x in sites]))
        check_sites_availability(config, sites)
    except Exception as ex:
        logger.exception(ex)
