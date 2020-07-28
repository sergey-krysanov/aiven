from datetime import datetime
import pytz
import psycopg2
import collections
from common.logger import get_logger

logger = get_logger('db_model')

Site = collections.namedtuple('Site', 'id url regexps')
Regexp = collections.namedtuple('Regexp', 'id regexp')

def ts_to_utc_(ts):
    """ Converts time since epoch to UTC string """
    return str(datetime.fromtimestamp(ts, tz=pytz.utc))


def get_failed_id_list_(ids):
    if len(ids) == 0:
        return "(0) LIMIT 0"
    return ", ".join(["(" + str(x) + ")" for x in ids])


def get_insert_sql_(v):
    sql = """
        WITH metrics_insert AS (
            INSERT INTO metrics 
            (site_id, ts, http_code, response_time_ms, regexp_check_failed) 
            VALUES 
            ({site_id}, '{ts}', {status_code}, {response_time_ms},
            {regexp_check_failed}) 
            RETURNING id AS metric_id
        ), data (regexp_check_id) AS ( VALUES {failed_id_list} )
        INSERT INTO failed_checks
        (metric_id, regexp_check_id)
        SELECT metric_id, regexp_check_id
        FROM metrics_insert CROSS JOIN data
        """
    return sql.format(
        site_id = v['site_id'],
        ts = ts_to_utc_(v['ts']),
        status_code = v['status_code'],
        response_time_ms = v['response_time_ms'],
        regexp_check_failed = len(v['failed_regexps']) > 0,
        failed_id_list = get_failed_id_list_(v['failed_regexps']))


class DbModel(object):
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __del__(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.prepare_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        self.connection = None

    def prepare_connection(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(**self.config['pg'])

    def get_sites_list(self, group_id):
        try:
            self.prepare_connection()
            with self.connection.cursor() as cur:
                sql = "SELECT sites.id as site_id, url, " \
                    " regexp_checks.id as regexp_id, regexp " \
                    " from sites LEFT JOIN" \
                    " regexp_checks on sites.id=regexp_checks.site_id" \
                    " WHERE group_id='{group_id}';"
                cur.execute(sql.format(group_id=group_id))
                rows = cur.fetchall()
                id_to_site = {}
                for r in rows:
                    site_id = r[0]
                    default_site = Site(id=site_id, url=r[1], regexps=[])
                    site = id_to_site.get(site_id, default_site)
                    if r[2] is not None:
                        site.regexps.append(Regexp(id=r[2], regexp=r[3]))
                    id_to_site[site_id] = site
                return id_to_site.values()
        except Exception as ex:
            logger.exception(ex)
            raise

    def save_metrics(self, values):
        if not values:
            return

        try:
            sql = "; ".join([get_insert_sql_(v) for v in values])
            self.prepare_connection()
            with self.connection.cursor() as cur:
                cur.execute(sql)
            self.connection.commit()
        except Exception as ex:
            logger.exception(ex)
            raise
