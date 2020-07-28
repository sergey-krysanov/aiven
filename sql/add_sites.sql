BEGIN;

INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/200', 'group_01');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/201', 'group_01');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/400', 'group_01');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/404', 'group_01');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/503', 'group_01');
INSERT INTO sites (url, group_id) VALUES ('https://httpstat.us/200', 'group_01');

INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/202', 'group_02');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/401', 'group_02');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/403', 'group_02');
INSERT INTO sites (url, group_id) VALUES ('http://httpstat.us/500', 'group_02');

INSERT INTO regexp_checks (site_id, regexp) SELECT id, '200 OK' FROM sites WHERE url='http://httpstat.us/200';
INSERT INTO regexp_checks (site_id, regexp) SELECT id, '^Failure' FROM sites WHERE url='http://httpstat.us/201';

COMMIT;
