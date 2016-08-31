````
                                    +---------------------------------------------+
                                    |Listing                                      |    +--------------------+
                                    +---------------------------------------------+    |DocUrl              |        +---------------------------+
     +-----------+                  |title                                        |    +--------------------+        |Notification               |
     |Category   |                  |approved_date                                |    |name                |        +---------------------------+
     +-----------+                  |edited_date                                  |    |url                 |        |created_date               |
     |title      |                  |agency = (fk-Agency)                         |    |listing (fk-Listing)|        |message                    |
     |description|                  |listing_type (fk-ListingType)                |    +--------------------+        |expires_date               |
     +-----------+                  |description                                  |                                  |author (fk-Profile)        |
                                    |launch_url                                   |                                  |dismissed_by (m2m-Profile) |
                                    | version_name                                |                                  |listing (fk-Listing)       |
                                    |unique_name                                  |                                  |agency (fk-Agency          |
           +-----+                  |small_icon = (fk-Image)                      |                                  |peer (json)                |
           |Tag  |                  |large_icon = (fk-Image)                      |                                  | fk-Profile                |
           +-----+                  |banner_icon = (fk-Image)                     |                                  | folder_name               |
           |name |                  |large_banner_icon = (fk-Image)               |                                  | bookmark_listing_ids      |
           +-----+                  |what_is_new                                  |                                  +---------------------------+
                                    |description_short                            |
                                    |requirements                                 |
                                    |approval_status                              |      +------------------------------+
+---------------+                   | * IN_PROGRESS                               |      |Contact                       |      +------------+
|ImageType      |                   | * PENDING                                   |      +------------------------------+      |ContactType |
+---------------+                   | * APPROVED_ORG                              |      |secure_phone                  |      +------------+
|name           |                   | * APPROVED                                  |      |unsecure_phone                |      |name        |
|max_size_bytes |                   | * REJECTED                                  |      |email                         |      |required    |
|max_width      |                   | * DELETED                                   |      |name                          |      +------------+
|max_height     |                   |is_enabled                                   |      |organization                  |
|min_width      |                   |is_featured                                  |      |contact_type (fk-ContactType) |
+---------------+                   |is_deleted                                   |      +------------------------------+
                                    |avg_rate                                     |
                                    |total_votes                                  |
+-------------------------+         |total_rate5                                  |                                                +-------------+
|Image                    |         |total_rate4                                  |                                                |ChangeDetail |
+-------------------------+         |total_rate3                                  |       +----------------------------------+     +-------------+
|uuid                     |         |total_rate2                                  |       |ListingActivity                   |     |field_name   |
|security_marking         |         |total_rate1                                  |       +----------------------------------+     | old_value   |
|file_extension           |         |total_reviews                                |       |action                            |     |new_value    |
|image_type (fk-ImageType)|         |iframe_compatible                            |       | * CREATED                        |     |             |
+-------------------------+         |contacts (mtm-Contact)                       |       | * MODIFIED                       |     +-------------+
                                    |owners (mtm-Profile)                         |       | * SUBMITTED                      |
                                    |categories (mtm-Category)                    |       | * APPROVED_ORG                   |
+---------------+                   |tags (mtm-Tag)                               |       | * APPROVED                       |
|Intent         |                   |required_listings  (fk-Listing)              |       | * REJECTED                       |
+---------------+                   |last_activity  (1t1-ListingActivity          |       | * ENABLED                        |
|action         |                   |current_rejection  (1t1-ListingActivity)     |       | * DISABLED                       |
|media_type     |                   |intents (mtm-Intent')                        |       | * DELETED                        |
|label          |                   |security_marking                             |       | * REVIEW_EDITED                  |     +----------------------+
|icon (fk-Image)|                   |is_private                                   |       | * REVIEW_DELETED                 |     |Screenshot            |
+---------------+                   |is_bookmarked (dy)                           |       |activity_date                     |     +----------------------+
                                    +---------------------------------------------+       |description                       |     |small_image (fk|Image)|
                                                                                          |author (fk-Profile)               |     |large_image (fk-Image)|
     +------------------------+                                                           |listing (fk-Listing)              |     |listing (fk-Listing)  |
     |ApplicationLibraryEntry |                                                           |change_details (mtm-ChangeDetail) |     +----------------------+
     +------------------------+                                                           +----------------------------------+
     |folder (folder_name)    |
     |owner (fk-Profile)      |
     |listing (fk-Listing)    |
     +------------------------+     +------------------------------------------+                                           +---------------+
                                    |Profile                                   |                                           |Agency         |
                                    +------------------------------------------+                                           +---------------+
                                    |display_name                              |                                           |title          |
                                    |bio                                       |                                           |icon (fk-Image)|
 +------------+                     |center_tour_flag                          |                                           |short_name     |
 |ListingType |                     |hud_tour_flag                             |                +--------------------+     +---------------+
 +------------+                     |webtop_tour_flag                          |                |Review              |
 |title       |                     |dn                                        |                +--------------------+
 |description |                     |issuer_dn                                 |                |text                |
 +------------+                     |auth_expires                              |                |rate                |
                                    |organizations (mm-Agency)                 |                |listing (fk-Listing)|
                                    |stewarded_organizations (mm-Agency)       |                |author (fk-Profile) |
                                    |access_control                            |                |edited_date         |
                                    |user (1t1-DjangoUser)                     |                +--------------------+
                                    +------------------------------------------+
````
