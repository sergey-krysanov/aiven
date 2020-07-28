from datetime import datetime
import collections
import psycopg2
import pytz
from common.logger import get_logger

logger = get_logger('db_model')

Site = collections.namedtuple('Site', 'id url regexps')
Regexp = collections.namedtuple('Regexp', 'id regexp')


def _ts_to_utc(ts):
    """ Converts time since epoch to UTC string """
    return str(datetime.fromtimestamp(ts, tz=pytz.utc))


def _get_failed_id_list(ids):
    if not ids:
        return "(0) LIMIT 0"
    return ", ".join(["(" + str(x) + ")" for x in ids])


def _get_insert_sql(v):
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
        site_id=v['site_id'],
        ts=_ts_to_utc(v['ts']),
        status_code=v['status_code'],
        response_time_ms=v['response_time_ms'],
        regexp_check_failed=len(v['failed_regexps']) > 0,
        failed_id_list=_get_failed_id_list(v['failed_regexps']))


class DbModel(object):
    """ DbModel

        Takes care of storing and loading data structures
        to PostgreSQL database
    """
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __del__(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self._prepare_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        self.connection = None

    def _prepare_connection(self):
        """ Creates a new connection if it was not
            created yet or was closed
        """
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(**self.config['pg'])

    def get_sites_list(self, group_name):
        """ Returns list of sites to check for specified group

            Arguments:
               group_name(str): group name to filter result sites
        """
        try:
            self._prepare_connection()
            with self.connection.cursor() as cur:
                sql = "SELECT sites.id as site_id, url, " \
                    " regexp_checks.id as regexp_id, regexp " \
                    " from sites LEFT JOIN" \
                    " regexp_checks on sites.id=regexp_checks.site_id" \
                    " WHERE {group_condition};"
                if group_name is None:
                    group_condition = "group_name is NULL"
                else:
                    group_condition = "group_name='{group_name}'" \
                        .format(group_name=group_name)
                cur.execute(sql.format(group_condition=group_condition))
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
        """ Save metric values to database

            Arguments:
                values: list of dictionaries with metrics
        """
        if not values:
            return

        try:
            sql = "; ".join([_get_insert_sql(v) for v in values])
            self._prepare_connection()
            with self.connection.cursor() as cur:
                cur.execute(sql)
            self.connection.commit()
        except Exception as ex:
            logger.exception(ex)
            raise
