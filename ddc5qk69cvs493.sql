-- Adminer 4.6.3-dev PostgreSQL dump

\connect "ddc5qk69cvs493";

DROP TABLE IF EXISTS "checkins";
DROP SEQUENCE IF EXISTS checkins_id_seq;
CREATE SEQUENCE checkins_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."checkins" (
    "id" integer DEFAULT nextval('checkins_id_seq') NOT NULL,
    "loc_id" integer NOT NULL,
    "cin_userid" integer NOT NULL,
    "comments" character varying,
    CONSTRAINT "checkins_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "checkins_cin_userid_fkey" FOREIGN KEY (cin_userid) REFERENCES users(id) NOT DEFERRABLE,
    CONSTRAINT "checkins_loc_id_fkey" FOREIGN KEY (loc_id) REFERENCES locations(id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "locations";
DROP SEQUENCE IF EXISTS locations_id_seq;
CREATE SEQUENCE locations_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."locations" (
    "id" integer DEFAULT nextval('locations_id_seq') NOT NULL,
    "city" character varying NOT NULL,
    "zipcode" character varying NOT NULL,
    "statecode" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "locations_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_username_key" UNIQUE ("username")
) WITH (oids = false);


-- 2018-07-12 20:11:59.830022+00
