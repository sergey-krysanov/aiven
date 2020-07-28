import threading
from producer.site_checker import SiteChecker
from common.db_model import Site, Regexp

SITE_ID = 123


def test_site_checker():
    """ This is a basic test for class SiteChecker """

    regexps = [Regexp(id=0, regexp="200 OK"),
               Regexp(id=1, regexp=".*OK$"),
               Regexp(id=2, regexp="^200"),
               Regexp(id=3, regexp="^Failure")]
    site = Site(id=SITE_ID,
                url="http://httpstat.us/200",
                regexps=regexps)
    checker = SiteChecker(site, 60)
    completed = threading.Event()

    test = {SITE_ID: None}

    def on_check_complete_cb(site_id, status_code, response_time, failed_regexps):
        """ Callback function provided to SiteChecker  """
        test[site_id] = {'status_code': status_code,
                         'response_time_ms': response_time,
                         'failed_regexps': failed_regexps}
        completed.set()

    checker.start(on_check_complete_cb)

    while not completed.isSet():
        completed.wait(3)
        break

    checker.stop()

    assert len(test) == 1
    assert test[SITE_ID] is not None
    assert test[SITE_ID]['status_code'] == 200
    assert test[SITE_ID]['response_time_ms'] is not None
    assert test[SITE_ID]['response_time_ms'] > 0
    print("Failed: {}".format(test[SITE_ID]['failed_regexps']))
    assert test[SITE_ID]['failed_regexps'] == [3]
