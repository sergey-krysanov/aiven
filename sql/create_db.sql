BEGIN;

DROP TABLE IF EXISTS failed_checks;
DROP TABLE IF EXISTS regexp_checks;
DROP TABLE IF EXISTS metrics;
DROP TABLE IF EXISTS sites;


CREATE TABLE sites (
    id bigserial PRIMARY KEY,
    url varchar UNIQUE NOT NULL,
    group_id varchar(64)
);

CREATE TABLE metrics (
    id bigserial PRIMARY KEY,
    site_id bigint NOT NULL,
    ts timestamptz NOT NULL,
    http_code int NOT NULL,
    response_time_ms int NOT NULL,
    regexp_check_failed bool NOT NULL,

    CONSTRAINT fk_site_id  FOREIGN KEY (site_id)  REFERENCES sites (id)
);


CREATE TABLE regexp_checks (
    id bigserial PRIMARY KEY,
    site_id bigint NOT NULL,
    regexp varchar UNIQUE NOT NULL,

    CONSTRAINT fk_site_id  FOREIGN KEY (site_id)  REFERENCES sites (id)
);

CREATE TABLE failed_checks (
    id bigserial PRIMARY KEY,
    metric_id bigint NOT NULL,
    regexp_check_id bigint,

    CONSTRAINT fk_metric_id  FOREIGN KEY (metric_id)  REFERENCES metrics (id),
    CONSTRAINT fk_regexp_check_id  FOREIGN KEY (regexp_check_id)  REFERENCES regexp_checks (id)
);

COMMIT;
