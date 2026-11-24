CREATE TABLE vehicles(id serial PRIMARY KEY, plate text UNIQUE NOT NULL);
CREATE TABLE drivers(id serial PRIMARY KEY,name text NOT NULL);
CREATE TABLE shipments(id serial PRIMARY KEY,destination text NOT NULL,status text NOT NULL DEFAULT 'pending',vehicle_id int REFERENCES vehicles,driver_id int REFERENCES drivers);
CREATE UNIQUE INDEX active_vehicle ON shipments(vehicle_id) WHERE status IN ('assigned','in_transit');
CREATE UNIQUE INDEX active_driver ON shipments(driver_id) WHERE status IN ('assigned','in_transit');
CREATE TABLE gps(event_id text PRIMARY KEY,vehicle_id int REFERENCES vehicles NOT NULL,lat double precision CHECK(lat BETWEEN -90 AND 90),lon double precision CHECK(lon BETWEEN -180 AND 180),recorded_at timestamptz NOT NULL);
CREATE INDEX gps_latest ON gps(vehicle_id,recorded_at DESC,event_id DESC);
INSERT INTO vehicles(plate) VALUES ('DEMO-001'); INSERT INTO drivers(name) VALUES ('Demo Driver');
