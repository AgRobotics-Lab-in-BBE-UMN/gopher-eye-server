-- Drop all foreign key constraints first
ALTER TABLE "site" DROP CONSTRAINT IF EXISTS "site_permission_fkey";
ALTER TABLE "record" DROP CONSTRAINT IF EXISTS "record_site_id_fkey";
ALTER TABLE "sample" DROP CONSTRAINT IF EXISTS "sample_record_id_fkey";
ALTER TABLE "sample" DROP CONSTRAINT IF EXISTS "sample_created_by_fkey";
ALTER TABLE "membership" DROP CONSTRAINT IF EXISTS "membership_user_id_fkey";
ALTER TABLE "membership" DROP CONSTRAINT IF EXISTS "membership_group_id_fkey";
ALTER TABLE "mask" DROP CONSTRAINT IF EXISTS "mask_image_id_fkey";
ALTER TABLE "bounding_box" DROP CONSTRAINT IF EXISTS "bounding_box_image_id_fkey";
ALTER TABLE "ownership" DROP CONSTRAINT IF EXISTS "ownership_group_id_fkey";
ALTER TABLE "ownership" DROP CONSTRAINT IF EXISTS "ownership_record_id_fkey";

-- Drop all tables
DROP TABLE IF EXISTS "ownership";
DROP TABLE IF EXISTS "bounding_box";
DROP TABLE IF EXISTS "mask";
DROP TABLE IF EXISTS "membership";
DROP TABLE IF EXISTS "sample";
DROP TABLE IF EXISTS "record";
DROP TABLE IF EXISTS "site";
DROP TABLE IF EXISTS "group";
DROP TABLE IF EXISTS "user";