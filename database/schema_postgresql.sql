-- schema_postgresql.sql
create sequence bulletin_batches_batch_id_seq
    as integer;

create sequence bulletin_batches_batch_id_seq1
    as integer;

create table if not exists bulletin_batches_backup
(
    batch_id       integer default nextval('bulletin_batches_batch_id_seq'::regclass) not null,
    scraped        boolean                                                            not null,
    scrapable      boolean                                                            not null,
    date           date,
    date_scraped   timestamp,
    bulletin_count integer,
    note           text,
    constraint bulletin_batches_pkey
        primary key (batch_id)
);

alter sequence bulletin_batches_batch_id_seq owned by bulletin_batches_backup.batch_id;

create table if not exists bulletins_raw_backup
(
    batch_id        integer not null,
    bulletin_number integer not null,
    date            date,
    description     text,
    processed       boolean,
    constraint bulletins_raw_pkey
        primary key (batch_id, bulletin_number),
    constraint bulletins_raw_batch_id_fkey
        foreign key (batch_id) references bulletin_batches_backup
);

create table if not exists bulletins_processed_backup
(
    batch_id                integer not null,
    bulletin_number         integer not null,
    date                    date,
    description             text,
    category                varchar,
    sub_category            varchar,
    location_happening_text varchar,
    lat_happening           double precision,
    lon_happening           double precision,
    location_reporting_text varchar,
    lat_reporting           double precision,
    lon_reporting           double precision,
    event_time              timestamp,
    ai_confidence           double precision,
    processed_timestamp     timestamp,
    processor_version       varchar,
    notes                   text,
    constraint bulletins_processed_pkey
        primary key (batch_id, bulletin_number),
    constraint bulletins_processed_batch_id_bulletin_number_fkey
        foreign key (batch_id, bulletin_number) references bulletins_raw_backup
);

create table if not exists bulletin_batches
(
    batch_id       integer default nextval('bulletin_batches_batch_id_seq1'::regclass) not null,
    scraped        boolean                                                             not null,
    scrapable      boolean                                                             not null,
    date           date,
    date_scraped   timestamp,
    bulletin_count integer,
    note           text,
    constraint bulletin_batches_pkey1
        primary key (batch_id)
);

alter sequence bulletin_batches_batch_id_seq1 owned by bulletin_batches.batch_id;

create table if not exists bulletins_raw
(
    batch_id        integer not null,
    bulletin_number integer not null,
    date            date,
    description     text,
    processed       boolean,
    constraint bulletins_raw_pkey1
        primary key (batch_id, bulletin_number),
    constraint bulletins_raw_batch_id_fkey1
        foreign key (batch_id) references bulletin_batches
);

create table if not exists bulletins_processed
(
    batch_id            integer not null,
    bulletin_number     integer not null,
    date                date,
    description         text,
    category            varchar,
    sub_category        varchar,
    location_report     varchar,
    lat_report          double precision,
    lon_report          double precision,
    location_event      varchar,
    lat_event           double precision,
    lon_event           double precision,
    event_time          timestamp,
    processed_timestamp timestamp,
    processor_version   varchar,
    notes               text,
    constraint bulletins_processed_pkey1
        primary key (batch_id, bulletin_number),
    constraint bulletins_processed_batch_id_bulletin_number_fkey1
        foreign key (batch_id, bulletin_number) references bulletins_raw
);
