import time
from common.db_model import DbModel
from common.config import get_config


def get_item(site_id, timestamp, status_code, response_time_ms, failed_regexps):
    return {
        'site_id': site_id,
        'ts': timestamp,
        'status_code': status_code,
        'response_time_ms': response_time_ms,
        'failed_regexps': failed_regexps
    }

def test_get_sites():
    config = get_config()
    db_model = DbModel(config)
    sites = db_model.get_sites_list("group_01")
    assert len(sites) == 6
    for site in sites:
        if site.url == 'http://httpstat.us/200':
            assert len(site.regexps) == 1
            assert site.regexps[0].regexp == '200 OK'
        elif site.url == 'http://httpstat.us/201':
            assert len(site.regexps) == 1
            assert site.regexps[0].regexp == '^Failure'


def test_save_metrics_empty():
    config = get_config()
    db_model = DbModel(config)
    db_model.save_metrics([])


def test_save_metrics_non_empty():
    config = get_config()
    db_model = DbModel(config)
    values = [get_item(1, time.time(), 200, 8, []),
              get_item(1, time.time(), 500, 8, [1, 2])]
    db_model.save_metrics(values)
