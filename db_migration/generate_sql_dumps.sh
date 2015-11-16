#!/usr/bin/env bash

# set up to not require password for mysqldump: http://stackoverflow.com/questions/9293042/mysqldump-without-the-password-prompt
mysqldump -u ozp ozp category > category.sql --complete-insert --hex-blob
mysqldump -u ozp ozp agency > agency.sql --complete-insert --hex-blob
mysqldump -u ozp ozp profile > profile.sql --complete-insert --hex-blob
mysqldump -u ozp ozp type > type.sql --complete-insert --hex-blob
mysqldump -u ozp ozp contact_type > contact_type.sql --complete-insert --hex-blob
mysqldump -u ozp ozp profile_agency > profile_agency.sql --complete-insert --hex-blob
mysqldump -u ozp ozp iwc_data_object > iwc_data_object.sql --complete-insert --hex-blob
mysqldump -u ozp ozp notification > notification.sql --complete-insert --hex-blob
mysqldump -u ozp ozp profile_dismissed_notifications > profile_dismissed_notifications.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing > listing.sql --complete-insert --hex-blob
mysqldump -u ozp ozp doc_url > doc_url.sql --complete-insert --hex-blob
mysqldump -u ozp ozp screenshot > screenshot.sql --complete-insert --hex-blob
mysqldump -u ozp ozp contact > contact.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing_category > listing_category.sql --complete-insert --hex-blob
mysqldump -u ozp ozp item_comment > item_comment.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing_profile > listing_profile.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing_snapshot > listing_snapshot.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing_tags > listing_tags.sql --complete-insert --hex-blob
mysqldump -u ozp ozp application_library_entry > application_library_entry.sql --complete-insert --hex-blob
mysqldump -u ozp ozp change_detail > change_detail.sql --complete-insert --hex-blob
mysqldump -u ozp ozp listing_activity > listing_activity.sql --complete-insert --hex-blob
mysqldump -u ozp ozp modify_relationship_activity > modify_relationship_activity.sql --complete-insert --hex-blob
mysqldump -u ozp ozp rejection_activity > rejection_activity.sql --complete-insert --hex-blob
mysqldump -u ozp ozp rejection_listing > rejection_listing.sql --complete-insert --hex-blob
mysqldump -u ozp ozp relationship_activity_log > relationship_activity_log.sql --complete-insert --hex-blob

# gather images
IMG_DIR=/usr/share/tomcat/images
IMG_DEST=../images
find $IMG_DIR -type f -exec cp {} $IMG_DEST \;
