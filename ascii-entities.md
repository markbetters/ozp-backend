````
                                                 +-----------+     +------------+   +-----+   +--------------------+
                                                 |Category   |     |ListingType |   |Tag  |   |DocUrl              |
                                                 +-----------+     +------------+   +-----+   +--------------------+
                                                 |title      |     |title       |   |name |   |name                |
           +---------------+                     |description|     |description |   +--+--+   |url                 |
           |ImageType      |                     +----------++     +------+-----+      |      |listing (fk-Listing)|
           +---------------+                                |             |            |      +------+-------------+
           |name           |                                |             |            |             |
           |max_size_bytes |                                |             |            |             |
           |max_width      +- +-------------------------+   |       +-----+------------+-------------+------------+
           |max_height     |  |Image                    |   +-------+Listing                                      |    +------------+
           |min_width      |  +-------------------------+           +---------------------------------------------+    |ContactType |
           +---------------+  |uuid                     |           |title                                        |    +------------+
                              |security_marking         |           |approved_date                                |    |name        |
                              |file_extension           |           |edited_date                                  |    |required    |
                +-------------+image_type (fk-ImageType)|           |agency = (fk-Agency)                         |    +----------+-+
                |             +--+------------+---------+           |listing_type (fk-ListingType)                |               |
                |                |            |                     |description                                  |     +---------+--------------------+
                |                |   +--------+------+              |launch_url                                   |     |Contact                       |
                |                |   |Intent         |              | version_name                                |     +------------------------------+
                |                |   +---------------+              |unique_name                                  |     |secure_phone                  |
                |                |   |action         |              |small_icon = (fk-Image)                      |     |unsecure_phone                |
                |                |   |media_type     |              |large_icon = (fk-Image)                      |     |email                         |
                |                |   |label          +--------------+banner_icon = (fk-Image)                     +-----+name                          |
                |                |   |icon (fk-Image)|              |large_banner_icon = (fk-Image)               |     |organization                  |
                |                |   +---------------+              |what_is_new                                  |     |contact_type (fk-ContactType) |
                |                |                                  |description_short                            |     +------------------------------+
                |                |                                  |requirements                                 |
                |             +--+-------------------+              |approval_status                              |       +-------------+
                |             |Screenshot            |              | * IN_PROGRESS                               |       |ChangeDetail |
                |             +----------------------+              | * PENDING                                   |       +-------------+
    +-----------+---+         |small_image (fk|Image)+--------------+ * APPROVED_ORG                              |       |field_name   |
    |Agency         |         |large_image (fk-Image)|              | * APPROVED                                  |       | old_value   |
    +---------------+         |listing (fk-Listing)  |              | * REJECTED                                  |       |new_value    |
    |title          |         +----------------------+              | * DELETED                                   |       |             |
    |icon (fk-Image)|                                               |is_enabled                                   |       +-------+-----+
+---+short_name     +-----------------------------------------------+is_featured                                  |               |
|   +-----------+---+                                               |is_deleted                                   |               |
|               |                                                   |avg_rate                                     |               |
|               |                                                   |total_votes                                  |               |
|       +-------+-------------------+                               |total_rate5                                  |               |
|       |Notification               |                               |total_rate4                                  |               |
|       +---------------------------+                               |total_rate3                                  |               |
|       |created_date               |                               |total_rate2                                  |               |
|       |message                    +-------------------------------+total_rate1                                  |               |
|       |expires_date               |                               |total_reviews                                |         +-----+----------------------------+
|       |author (fk-Profile)        |                               |iframe_compatible                            |         |ListingActivity                   |
|       |dismissed_by (m2m-Profile) |                               |contacts (mtm-Contact)                       |         +----------------------------------+
|       |listing (fk-Listing)       |     +--------------------+    |owners (mtm-Profile)                         |         |action                            |
|       |agency (fk-Agency          |     |Review              |    |categories (mtm-Category)                    |         | * CREATED                        |
|       |peer (json)                |     +--------------------+    |tags (mtm-Tag)                               |         | * MODIFIED                       |
|       | fk-Profile                |     |text                |    |required_listings  (fk-Listing)              |         | * SUBMITTED                      |
|       | folder_name               |     |rate                |    |last_activity  (1t1-ListingActivity          +---------+ * APPROVED_ORG                   |
|       | bookmark_listing_ids      |     |listing (fk-Listing)|    |current_rejection  (1t1-ListingActivity)     |         | * APPROVED                       |
|       +-----------------------+---+     |author (fk-Profile) |    |intents (mtm-Intent')                        |         | * REJECTED                       |
|                               |         |edited_date         |    |security_marking                             |         | * ENABLED                        |
|                               |         +-+------------------+    |is_private                                   |         | * DISABLED                       |
|                               |           |                       |is_bookmarked (dy)                           |         | * DELETED                        |
|                               |           |        +----------------------+-------------------------------------+         | * REVIEW_EDITED                  |
|                               |           |        |                      |                                               | * REVIEW_DELETED                 |
|  +------------------------+   |           |        |                      |                                               |activity_date                     |
|  |ApplicationLibraryEntry |   |           |        |                      |                                               |description                       |
|  +------------------------+   |           |        |           +----------+-------------------------------+               |author (fk-Profile)               |
|  |folder (folder_name)    |   |           |        |           |Profile                                   +---------------+listing (fk-Listing)              |
|  |owner (fk-Profile)      +------------------------+           +------------------------------------------+               |change_details (mtm-ChangeDetail) |
|  |listing (fk-Listing)    |   |           |                    |display_name                              |               +----------------------------------+
|  +---------------+--------+   |           |                    |bio                                       |
|                  |            |           |                    |center_tour_flag                          |
|                  |            +--------------------------------+hud_tour_flag                             |
|                  |                        +--------------------+webtop_tour_flag                          |
|                  |                                             |dn                                        |
|                  |                                             |issuer_dn                                 |
|                  +---------------------------------------------+auth_expires                              |
|                                                                |organizations (mm-Agency)                 |
|                                                                |stewarded_organizations (mm-Agency)       |
|                                                                |access_control                            |
+----------------------------------------------------------------+user (1t1-DjangoUser)                     |
                                                                 +------------------------------------------+
````
