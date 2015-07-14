"""
constants used throughout the app
"""
MAX_URL_SIZE = 2083  # see http://support.microsoft.com/kb/208427
URL_REGEX = r'^(https|http|ftp|sftp|file)://.*$'
# original url regex: /^(((https|http|ftp|sftp|file):\/)|(\/)){1}(.*)+$/
MAX_VALUE_LENGTH = 4000
# TODO
PHONE_REGEX = r'\d'
# original phone regex: /(^\+\d((([\s.-])?\d+)?)+$)|(^(\(\d{3}\)\s?|^\d{3}[\s.-]?)?\d{3}[\s.-]?\d{4}$)/
# TODO
EMAIL_REGEX = r'\w'
# original email regex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/
# TODO
INTENT_ACTION_REGEX = r'\w'
# original intent action regex: /^[-\w]([-\w\+\$\!\#\&\-\_\^\.]{1,63})?$/
# TODO
MEDIA_TYPE_REGEX = r'\w'
# original media type regex: /^[-\w]([-\w\+\$\!\#\&\-\_\^\.]{1,63})?\/[-\w]([-\w\+\$\!\#\&\-\_\^\.]{1,63})?$/

# valid image types
VALID_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']