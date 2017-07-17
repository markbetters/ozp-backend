import logging
import json

from django.contrib.auth.models import User

from ozpcenter import models
from ozpcenter import model_access

logger = logging.getLogger('ozp.' + str(__name__))

def cas_callback(tree):
    username = tree[0][0].text
    count = User.objects.filter(username=username).count()
    if count == 0:
      logger.debug('Creating new user ' + username)
      usergroups = ['USER']
      email = username+'@inc1.army.mil'
      displayname = username
      cn = username
      if len(tree[0]) > 1:
        for element in tree[0][1]:
          if element.tag.endswith('role_admin'):
             admin = element.text
             if admin == 'true':
               usergroups = ['APPS_MALL_STEWARD']
          elif element.tag.endswith('displayname'):
             displayname = element.text
          elif element.tag.endswith('userprincipalname'):
             email = element.text
          elif element.tag.endswith('cn'):
             cn = element.text
      logger.debug('GROUPS ARE: ' + str(usergroups))
      access_control = json.dumps({'clearances': ['UNCLASSIFIED']})
      organization = 'dcgs'
      user = models.Profile.create_user(username,
             email=email,
             display_name=displayname,
             access_control=access_control,
             organizations=[organization],
             groups=usergroups,
             dn=cn
      )
    else:
     logger.debug('User for username: ' + username + ' already exists')
