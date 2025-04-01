CREATE TABLE "user" (
  "id" varchar PRIMARY KEY,
  "first_name" varchar,
  "last_name" varchar,
  "user_name" varchar,
  "email" varchar,
  "join_date" date,
  "last_login" date
);

CREATE TABLE "site" (
  "id" varchar PRIMARY KEY,
  "permission" varchar,
  "created_date" date,
  "gps_longitude" int,
  "gps_latitude" int,
  "description" varchar
);

CREATE TABLE "record" (
  "id" varchar PRIMARY KEY,
  "site_id" varchar,
  "created_by" varchar,
  "created_date" date
);

CREATE TABLE "sample" (
  "id" varchar PRIMARY KEY,
  "record_id" varchar,
  "created_date" date,
  "created_by" varchar,
  "image_url" varchar,
  "type" varchar,
  "processing_status" varchar
);

CREATE TABLE "group" (
  "id" varchar PRIMARY KEY,
  "type" varchar,
  "description" varchar
);

CREATE TABLE "membership" (
  "user_id" varchar,
  "group_id" varchar
);

CREATE TABLE "mask" (
  "sample_id" varchar,
  "mask" varchar,
  "confidence" int,
  "label" varchar
);

CREATE TABLE "bounding_box" (
  "sample_id" varchar,
  "box" varchar,
  "confidence" int,
  "label" varchar
);

CREATE TABLE "ownership" (
  "group_id" varchar,
  "record_id" varchar
);

ALTER TABLE "site" ADD FOREIGN KEY ("permission") REFERENCES "group" ("id");

ALTER TABLE "record" ADD FOREIGN KEY ("site_id") REFERENCES "site" ("id");

ALTER TABLE "record" ADD FOREIGN KEY ("created_by") REFERENCES "user" ("id");

ALTER TABLE "sample" ADD FOREIGN KEY ("record_id") REFERENCES "record" ("id");

ALTER TABLE "sample" ADD FOREIGN KEY ("created_by") REFERENCES "user" ("id");

ALTER TABLE "membership" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "membership" ADD FOREIGN KEY ("group_id") REFERENCES "group" ("id");

ALTER TABLE "mask" ADD FOREIGN KEY ("sample_id") REFERENCES "sample" ("id");

ALTER TABLE "bounding_box" ADD FOREIGN KEY ("sample_id") REFERENCES "sample" ("id");

ALTER TABLE "ownership" ADD FOREIGN KEY ("group_id") REFERENCES "group" ("id");

ALTER TABLE "ownership" ADD FOREIGN KEY ("record_id") REFERENCES "record" ("id");
