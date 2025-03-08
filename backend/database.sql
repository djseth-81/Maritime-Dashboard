pragma foregin_keys = on;

-- WHAT OTHER CONSTRAINTS, checks, conditionals, etc???  
-- CHECK school_database.sql!


CREATE TABLE vessel (
    mmsi                integer UNIQUE NOT NULL primary key,
    vessel_name         varchar UNIQUE,
    callsign            varchar UNIQUE,
    timestamp           int,
    heading             int NOT NULL,
    speed               float NOT NULL, --units?
    current_status      varchar,
    voyage              varchar, -- array of port.ids?
    src                 varchar, -- not sure if I want this to be source.id, or if I want data such as "AIS".
    type                varchar DEFAULT 'UNKNOWN' check (type in ( 'UNKNOWN',
    'FISHING-LongLine',
    'FISHING-TROLLER',
    'TUG',
    'TANKER',
    'RECREATIONAL',
    'PUBLIC',
    )),
    anchored            boolean,
    length              int NOT NULL,
    width               int NOT NULL,
    current_cargo_wg    int NOT NULL,
    geom                geometry, -- Point
    -- Use these for geom?
    lat                 float NOT NULL,
    lon                 float NOT NULL,
    -- MarineCadastre: What is SOG, COG, IMO, Status, Draft, and what are Len/Width/Cargo units?
    -- GFW: What is "Course"?
    -- GFW Units (Are these necessary?)
    dist_from_shore     float,
    dist_from_port      float,
);

CREATE TABLE mock_ship (
    mmsi             int UNIQUE NOT NULL primary key,
    geom             geometry, -- Point
    lat              int NOT NULL,
    lon              int NOT NULL,
    heading          int NOT NULL,
    speed            float, --units?
    current_status   varchar,
    src              int NOT NULL,
    type             varchar DEFAULT 'UNKNOWN' check (type in ( 'UNKNOWN',
    'FISHING-LongLine',
    'FISHING-TROLLER',
    'TUG',
    'TANKER',
    'RECREATIONAL',
    'PUBLIC',
    )),
    anchored         boolean,
    length           int NOT NULL,
    width            int NOT NULL,
    current_cargo_wg int NOT NULL,
    -- Maybe calculate from lat,lon decided by user
    dist_from_shore  float,
    dist_from_port   float,
    FOREIGN KEY (src) REFERENCES user(id) ON DELETE CASCADE,
);

CREATE TABLE source (
    id          varchar UNIQUE NOT NULL primary key,
    name        varchar, -- GFW, MarineCadastre, Copernicus, COOP and Weather API (stations/regions), NCEI
    API         varchar,
    datums      varchar, -- "DATUM1 DATUM2 DATUM3 DATUM4 ... DATUMn"
    region      varchar, -- Operational jurisdiction of source (If database, note "database")
    timeZone    varchar,
    geom        geometry, -- Polygon
    type        varchar
);

CREATE TABLE geometry (
    id varchar NOT NULL primary key,
    geom geometry NOT NULL, -- Polygon
    src_id int NOT NULL,
    region varchar, -- US-IA
    type varchar check (type in ('MET',
                                 'MARINE',
                                 'EEZ',
                                 'PROTECTED',
                                 'RESTRICTED-FISH'),
    FOREIGN KEY (src_id) REFERENCES source(id)
);

CREATE TABLE port (
    id          integer NOT NULL primary key,
    name        varchar, -- reported Port ID, callsign (Like Airport ISO code?)?
    nationality varchar, -- Akin to region?
    lat         int NOT NULL,
    lon         int NOT NULL,
    geom        geometry, -- Polygon for jurisdiction?, Point for physical location?
);

CREATE TABLE meteorology (
    -- Would it be better to specify each type as an attr or as its own entity denoting type?
    id              integer NOT NULL primary key,
    src_id          int,
    lat             int,
    long            int,
    -- type varchar, -- Temp, humidity, wind speed, percipitation, etc.
    -- data varchar, -- data reported by source
    temp            float,
    humidity        float,
    wind_speed      float,
    wind_heading    float,
    percipitation   boolean,
    forecast        int[], -- array of other id's referencing this table. Forecasts entered as entities, and then updated if they match src_id, lat, lon, type, and timestamp?
    timestamp       int,
    geom            geometry, -- Polygon, or Point based off lat,lon values?
    event_id        int, -- if NULL, ignore
    region          varchar,
    FOREIGN KEY (src_id,region) REFERENCES source(id,region),
    FOREIGN KEY (event_id) REFERENCES event(id)
);

CREATE TABLE oceanography (
    id              integer NOT NULL primary key,
    src_id          int,
    lat             int,
    long            int,
    -- type varchar, -- wave height, water temp, "water physics"
    -- data varchar, -- data reported by source
    wave_height     float,
    water_temp      float,
    water_physics   varchar, -- what?
    timestamp       int,
    geom            geometry, -- Polygon
    region          varchar,
    event_id        int, -- if NULL, ignore
    FOREIGN KEY (src_id,region) REFERENCES source(id,region),
    FOREIGN KEY (event_id) REFERENCES event(id)
);

CREATE TABLE event (
    id          integer NOT NULL primary key,
    src_id      int,
    region      varchar,
    timestamp   int, -- timestamp event was reported to DB
    begin_time  int,
    end_time    int,
    active      boolean NOT NULL, -- Wonder if I can calulate this based off reported timestamp
    -- Would it be worth it to DELETE from DB automatically?
    type        varchar, -- Storm, geopolitical, shipping notice, oceanographic, etc.
    description varchar,
    FOREIGN KEY (src_id,region) REFERENCES source(id,region)
);

CREATE TABLE user (
    id          int NOT NULL primary key,
    uhash       varchar NOT NULL UNIQUE primary key,
    phash       varchar NOT NULL,
    first_name  varchar,
    last_name   varchar,
    email       varchar NOT NULL UNIQUE,
    last_logon  datetime NOT NULL DEFAULT 0,
    mfa         boolean NOT NULL DEFAULT false,
    countdown   int NOT NULL DEFAULT 90 CHECK (countdown > 0), -- set to 90 days?
    reg_date    datetime DEFAULT current_date,
    -- ALWAYS pull existing IDs when user login confirmed
    -- How to assign array datatype?
    presets     int[10], -- array of preset.id to ensure order of presets pulled
    FOREIGN KEY (presets) REFERENCES preset(id)
);

CREATE TABLE preset (
    id          int NOT NULL UNIQUE primary key,
    user_id     int NOT NULL, -- group by and then pull all presets assigned to user
    geom        geometry,
    filters     varchar, -- "FILTER1 FILTER 2 FILTER3 FILTER4 ... FILTERn"
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
);

