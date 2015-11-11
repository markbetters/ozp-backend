BEGIN;
CREATE TABLE "ozpcenter_imagetype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(64) NOT NULL UNIQUE,
    "max_size_bytes" integer NOT NULL,
    "max_width" integer NOT NULL,
    "max_height" integer NOT NULL,
    "min_width" integer NOT NULL,
    "min_height" integer NOT NULL
)
;
CREATE TABLE "ozpcenter_image" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "uuid" varchar(36) NOT NULL UNIQUE,
    "security_marking" varchar(1024) NOT NULL,
    "file_extension" varchar(16) NOT NULL,
    "image_type_id" integer NOT NULL REFERENCES "ozpcenter_imagetype" ("id")
)
;
CREATE TABLE "ozpcenter_tag" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(16) NOT NULL UNIQUE
)
;
CREATE TABLE "ozpcenter_agency" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(255) NOT NULL UNIQUE,
    "icon_id" integer REFERENCES "ozpcenter_image" ("id"),
    "short_name" varchar(8) NOT NULL UNIQUE
)
;
CREATE TABLE "ozpcenter_applicationlibraryentry" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "folder" varchar(255),
    "owner_id" integer NOT NULL,
    "listing_id" integer NOT NULL
)
;
CREATE TABLE "ozpcenter_category" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(50) NOT NULL UNIQUE,
    "description" varchar(255) NOT NULL
)
;
CREATE TABLE "ozpcenter_changedetail" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "field_name" varchar(255) NOT NULL,
    "old_value" varchar(4000),
    "new_value" varchar(4000)
)
;
CREATE TABLE "ozpcenter_contact" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "secure_phone" varchar(50),
    "unsecure_phone" varchar(50),
    "email" varchar(100) NOT NULL,
    "name" varchar(100) NOT NULL,
    "organization" varchar(100),
    "contact_type_id" integer NOT NULL
)
;
CREATE TABLE "ozpcenter_contacttype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(50) NOT NULL UNIQUE,
    "required" bool NOT NULL
)
;
CREATE TABLE "ozpcenter_docurl" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(255) NOT NULL,
    "url" varchar(2083) NOT NULL,
    "listing_id" integer NOT NULL
)
;
CREATE TABLE "ozpcenter_intent" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "action" varchar(64) NOT NULL,
    "media_type" varchar(129) NOT NULL,
    "label" varchar(255) NOT NULL,
    "icon_id" integer NOT NULL REFERENCES "ozpcenter_image" ("id")
)
;
CREATE TABLE "ozpcenter_review" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "text" varchar(4000),
    "rate" integer NOT NULL,
    "listing_id" integer NOT NULL,
    "author_id" integer NOT NULL,
    "edited_date" datetime NOT NULL,
    UNIQUE ("author_id", "listing_id")
)
;
CREATE TABLE "stewarded_agency_profile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "profile_id" integer NOT NULL,
    "agency_id" integer NOT NULL REFERENCES "ozpcenter_agency" ("id"),
    UNIQUE ("profile_id", "agency_id")
)
;
CREATE TABLE "agency_profile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "profile_id" integer NOT NULL,
    "agency_id" integer NOT NULL REFERENCES "ozpcenter_agency" ("id"),
    UNIQUE ("profile_id", "agency_id")
)
;
CREATE TABLE "ozpcenter_profile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "display_name" varchar(255) NOT NULL,
    "bio" varchar(1000) NOT NULL,
    "dn" varchar(1000) NOT NULL UNIQUE,
    "auth_expires" datetime NOT NULL,
    "access_control" varchar(1024) NOT NULL,
    "user_id" integer UNIQUE REFERENCES "auth_user" ("id")
)
;
CREATE TABLE "profile_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listing_id" integer NOT NULL,
    "profile_id" integer NOT NULL REFERENCES "ozpcenter_profile" ("id"),
    UNIQUE ("listing_id", "profile_id")
)
;
CREATE TABLE "intent_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listing_id" integer NOT NULL,
    "intent_id" integer NOT NULL REFERENCES "ozpcenter_intent" ("id"),
    UNIQUE ("listing_id", "intent_id")
)
;
CREATE TABLE "tag_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listing_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "ozpcenter_tag" ("id"),
    UNIQUE ("listing_id", "tag_id")
)
;
CREATE TABLE "category_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listing_id" integer NOT NULL,
    "category_id" integer NOT NULL REFERENCES "ozpcenter_category" ("id"),
    UNIQUE ("listing_id", "category_id")
)
;
CREATE TABLE "contact_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listing_id" integer NOT NULL,
    "contact_id" integer NOT NULL REFERENCES "ozpcenter_contact" ("id"),
    UNIQUE ("listing_id", "contact_id")
)
;
CREATE TABLE "ozpcenter_listing" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(255) NOT NULL,
    "approved_date" datetime,
    "edited_date" datetime NOT NULL,
    "agency_id" integer NOT NULL REFERENCES "ozpcenter_agency" ("id"),
    "listing_type_id" integer,
    "description" varchar(255),
    "launch_url" varchar(2083),
    "version_name" varchar(255),
    "unique_name" varchar(255) UNIQUE,
    "small_icon_id" integer REFERENCES "ozpcenter_image" ("id"),
    "large_icon_id" integer REFERENCES "ozpcenter_image" ("id"),
    "banner_icon_id" integer REFERENCES "ozpcenter_image" ("id"),
    "large_banner_icon_id" integer REFERENCES "ozpcenter_image" ("id"),
    "what_is_new" varchar(255),
    "description_short" varchar(150),
    "requirements" varchar(1000),
    "approval_status" varchar(255) NOT NULL,
    "is_enabled" bool NOT NULL,
    "is_featured" bool NOT NULL,
    "avg_rate" real NOT NULL,
    "total_votes" integer NOT NULL,
    "total_rate5" integer NOT NULL,
    "total_rate4" integer NOT NULL,
    "total_rate3" integer NOT NULL,
    "total_rate2" integer NOT NULL,
    "total_rate1" integer NOT NULL,
    "total_reviews" integer NOT NULL,
    "singleton" bool NOT NULL,
    "required_listings_id" integer REFERENCES "ozpcenter_listing" ("id"),
    "last_activity_id" integer UNIQUE,
    "current_rejection_id" integer UNIQUE,
    "security_marking" varchar(1024),
    "is_private" bool NOT NULL
)
;
CREATE TABLE "listing_activity_change_detail" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "listingactivity_id" integer NOT NULL,
    "changedetail_id" integer NOT NULL REFERENCES "ozpcenter_changedetail" ("id"),
    UNIQUE ("listingactivity_id", "changedetail_id")
)
;
CREATE TABLE "ozpcenter_listingactivity" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "action" varchar(128) NOT NULL,
    "activity_date" datetime NOT NULL,
    "description" varchar(2000),
    "author_id" integer NOT NULL REFERENCES "ozpcenter_profile" ("id"),
    "listing_id" integer NOT NULL REFERENCES "ozpcenter_listing" ("id")
)
;
CREATE TABLE "ozpcenter_screenshot" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "small_image_id" integer NOT NULL REFERENCES "ozpcenter_image" ("id"),
    "large_image_id" integer NOT NULL REFERENCES "ozpcenter_image" ("id"),
    "listing_id" integer NOT NULL REFERENCES "ozpcenter_listing" ("id")
)
;
CREATE TABLE "ozpcenter_listingtype" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(50) NOT NULL UNIQUE,
    "description" varchar(255) NOT NULL
)
;
CREATE TABLE "notification_profile" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "notification_id" integer NOT NULL,
    "profile_id" integer NOT NULL REFERENCES "ozpcenter_profile" ("id"),
    UNIQUE ("notification_id", "profile_id")
)
;
CREATE TABLE "ozpcenter_notification" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "created_date" datetime NOT NULL,
    "message" varchar(1024) NOT NULL,
    "expires_date" datetime NOT NULL,
    "author_id" integer NOT NULL REFERENCES "ozpcenter_profile" ("id"),
    "listing_id" integer REFERENCES "ozpcenter_listing" ("id")
)
;

COMMIT;

BEGIN;

CREATE TABLE "ozpiwc_dataresource" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "key" varchar(1024) NOT NULL,
    "entity" varchar(1048576),
    "content_type" varchar(1024),
    "username" varchar(128) NOT NULL,
    "pattern" varchar(1024),
    "permissions" varchar(1024),
    "version" varchar(1024),
    UNIQUE ("username", "key") )
;

COMMIT;
