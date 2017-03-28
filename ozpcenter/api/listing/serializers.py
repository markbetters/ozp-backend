"""
Listing Serializers
"""
import datetime
import logging
import pytz

from django.contrib import auth
from rest_framework import serializers

from ozpcenter import constants
from ozpcenter import models
from ozpcenter import errors
from plugins_util import plugin_manager
from plugins_util.plugin_manager import system_has_access_control
from plugins_util.plugin_manager import system_anonymize_identifiable_data
import ozpcenter.api.agency.model_access as agency_model_access
import ozpcenter.api.category.model_access as category_model_access
import ozpcenter.api.contact_type.model_access as contact_type_model_access
import ozpcenter.api.image.model_access as image_model_access
import ozpcenter.api.intent.model_access as intent_model_access
import ozpcenter.api.listing.model_access as model_access
import ozpcenter.api.profile.serializers as profile_serializers
import ozpcenter.model_access as generic_model_access
from ozpcenter.pubsub import dispatcher


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agency
        depth = 2
        fields = ('title', 'short_name')

        extra_kwargs = {
            'title': {'validators': []},
            'short_name': {'validators': []}
        }


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Image
        fields = ('url', 'id', 'security_marking')

        extra_kwargs = {
            'security_marking': {'validators': []},
            "id": {
                "read_only": False,
                "required": False,
            }
        }

    def validate_security_marking(self, value):
        # don't allow user to select a security marking that is above
        # their own access level
        profile = generic_model_access.get_profile(
            self.context['request'].user.username)

        if value:
            if not system_has_access_control(profile.user.username, value):
                raise serializers.ValidationError(
                    'Security marking too high for current user')
        else:
            raise serializers.ValidationError(
                'Security marking is required')

        return value


class ContactTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ContactType
        fields = ('name',)

        extra_kwargs = {
            'name': {'validators': []}
        }

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(ContactTypeSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        if anonymize_identifiable_data:
            ret['name'] = access_control_instance.anonymize_value('contact_type_name')

        return ret


class ContactSerializer(serializers.ModelSerializer):
    contact_type = ContactTypeSerializer()

    class Meta:
        model = models.Contact

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(ContactSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        if anonymize_identifiable_data:
            ret['secure_phone'] = access_control_instance.anonymize_value('secure_phone')
            ret['unsecure_phone'] = access_control_instance.anonymize_value('unsecure_phone')
            ret['secure_phone'] = access_control_instance.anonymize_value('secure_phone')
            ret['name'] = access_control_instance.anonymize_value('name')
            ret['organization'] = access_control_instance.anonymize_value('organization')
            ret['email'] = access_control_instance.anonymize_value('email')
        return ret


class ListingTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ListingType
        fields = ('title',)

        extra_kwargs = {
            'title': {'validators': []}
        }


class DocUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DocUrl
        fields = ('name', 'url')


class ScreenshotSerializer(serializers.ModelSerializer):
    small_image = ImageSerializer()
    large_image = ImageSerializer()

    class Meta:
        model = models.Screenshot
        fields = ('small_image', 'large_image')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('name',)

        extra_kwargs = {
            'name': {'validators': []}
        }


class ChangeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ChangeDetail


class ShortListingSerializer(serializers.HyperlinkedModelSerializer):
    agency = AgencySerializer(required=False)

    class Meta:
        model = models.Listing
        fields = ('unique_name', 'title', 'id', 'agency', 'small_icon', 'is_deleted')


class ListingActivitySerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()
    listing = ShortListingSerializer()
    change_details = ChangeDetailSerializer(many=True)

    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date', 'description', 'author', 'listing',
            'change_details')


class RejectionListingActivitySerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()

    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date', 'description', 'author')


class IntentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Intent
        # TODO: is action the right thing?
        fields = ('action',)

        extra_kwargs = {
            'action': {'validators': []}
        }


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ('title', 'description')

        extra_kwargs = {
            'title': {'validators': []}
        }


class CreateListingUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth.models.User
        fields = ('id', 'username',)

        extra_kwargs = {
            'username': {'validators': []}
        }

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(CreateListingUserSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        del ret['id']

        if anonymize_identifiable_data and not check_request_self:
            ret['username'] = access_control_instance.anonymize_value('username')

        return ret


class CreateListingProfileSerializer(serializers.ModelSerializer):
    user = CreateListingUserSerializer()

    class Meta:
        model = models.Profile
        fields = ('id', 'user', 'display_name')
        read_only = ('id', 'display_name')

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(CreateListingProfileSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        if anonymize_identifiable_data and not check_request_self:
            ret['display_name'] = access_control_instance.anonymize_value('display_name')

        return ret


class ListingIsBookmarked(serializers.ReadOnlyField):
    """
    Read Only Field to see if a listing is bookmarked
    """

    def to_native(self, obj):
        return obj


class ListingSerializer(serializers.ModelSerializer):
    is_bookmarked = ListingIsBookmarked()
    screenshots = ScreenshotSerializer(many=True, required=False)
    doc_urls = DocUrlSerializer(many=True, required=False)
    owners = CreateListingProfileSerializer(required=False, many=True)
    categories = CategorySerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    contacts = ContactSerializer(many=True, required=False)
    intents = IntentSerializer(many=True, required=False)
    small_icon = ImageSerializer(required=False, allow_null=True)
    large_icon = ImageSerializer(required=False, allow_null=True)
    banner_icon = ImageSerializer(required=False, allow_null=True)
    large_banner_icon = ImageSerializer(required=False, allow_null=True)
    agency = AgencySerializer(required=False)
    last_activity = ListingActivitySerializer(required=False, read_only=True)
    current_rejection = RejectionListingActivitySerializer(required=False,
        read_only=True)
    listing_type = ListingTypeSerializer(required=False, allow_null=True)

    class Meta:
        model = models.Listing
        depth = 2

    def to_representation(self, data):
        ret = super(ListingSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        if anonymize_identifiable_data:
            ret['contacts'] = []
        check_failed = []
        # owners
        if 'owners' in ret and not anonymize_identifiable_data:
            for owner in ret['owners']:
                user_dict = owner.get('user')
                user_username = None if user_dict is None else user_dict.get('username')

                # if not user_username:
                # raise serializers.ValidationError('Owner field requires correct format')

                owner_profile = generic_model_access.get_profile(user_username)
                # if not owner_profile:
                #    raise serializers.ValidationError('Owner Profile not found')

                # Don't allow user to select a security marking that is above
                # their own access level\
                try:
                    if system_has_access_control(owner_profile.user.username, ret.get('security_marking')) is False:
                        check_failed.append(owner_profile.user.username)
                        # raise serializers.ValidationError(owner_profile.user.username + 'User certificate is invalid')
                except Exception:
                    check_failed.append(owner_profile.user.username)

        ret['cert_issues'] = check_failed
        return ret

    @staticmethod
    def setup_eager_loading(queryset):
        # select_related foreign keys
        queryset = queryset.select_related('agency')
        queryset = queryset.select_related('small_icon')
        queryset = queryset.select_related('large_icon')
        queryset = queryset.select_related('banner_icon')
        queryset = queryset.select_related('large_banner_icon')
        queryset = queryset.select_related('required_listings')

        # prefetch_related many-to-many relationships
        queryset = queryset.prefetch_related('agency__icon')
        queryset = queryset.prefetch_related('screenshots')
        queryset = queryset.prefetch_related('screenshots__small_image')
        queryset = queryset.prefetch_related('screenshots__large_image')
        queryset = queryset.prefetch_related('doc_urls')
        queryset = queryset.prefetch_related('owners')
        queryset = queryset.prefetch_related('owners__user')
        queryset = queryset.prefetch_related('owners__organizations')
        queryset = queryset.prefetch_related('owners__stewarded_organizations')
        queryset = queryset.prefetch_related('categories')
        queryset = queryset.prefetch_related('tags')
        queryset = queryset.prefetch_related('contacts')
        queryset = queryset.prefetch_related('contacts__contact_type')
        queryset = queryset.prefetch_related('listing_type')
        queryset = queryset.prefetch_related('last_activity')
        queryset = queryset.prefetch_related('last_activity__change_details')
        queryset = queryset.prefetch_related('last_activity__author')
        queryset = queryset.prefetch_related('last_activity__author__organizations')
        queryset = queryset.prefetch_related('last_activity__author__stewarded_organizations')
        queryset = queryset.prefetch_related('last_activity__listing')
        queryset = queryset.prefetch_related('last_activity__listing__contacts')
        queryset = queryset.prefetch_related('last_activity__listing__owners')
        queryset = queryset.prefetch_related('last_activity__listing__owners__user')
        queryset = queryset.prefetch_related('last_activity__listing__categories')
        queryset = queryset.prefetch_related('last_activity__listing__tags')
        queryset = queryset.prefetch_related('last_activity__listing__intents')
        queryset = queryset.prefetch_related('current_rejection')
        queryset = queryset.prefetch_related('intents')
        queryset = queryset.prefetch_related('intents__icon')
        return queryset

    def validate(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        # logger.debug('inside ListingSerializer.validate', extra={'request':self.context.get('request')})
        profile = generic_model_access.get_profile(
            self.context['request'].user.username)

        # This checks to see if value exist as a key and value is not None
        if not data.get('title'):
            raise serializers.ValidationError('Title is required')

        if 'security_marking' not in data:
            raise serializers.ValidationError('Security Marking is Required')

        # Assign a default security_marking level if none is provided
        if not data.get('security_marking'):
            data['security_marking'] = constants.DEFAULT_SECURITY_MARKING

        if not access_control_instance.validate_marking(data['security_marking']):
            raise serializers.ValidationError('Security Marking Format is Invalid')

        # Don't allow user to select a security marking that is above
        # their own access level
        if not system_has_access_control(profile.user.username, data.get('security_marking')):
            raise serializers.ValidationError('Security marking too high for current user')

        # Don't allow 2nd-party user to be an submit/edit a listing
        if system_anonymize_identifiable_data(profile.user.username):
            raise serializers.ValidationError('Permissions are invalid for current profile')

        # TODO: errors.PermissionDenied instead of serializers.ValidationError

        data['description'] = data.get('description')
        data['launch_url'] = data.get('launch_url')
        data['version_name'] = data.get('version_name')
        data['unique_name'] = data.get('unique_name')
        data['what_is_new'] = data.get('what_is_new')
        data['description_short'] = data.get('description_short')
        data['requirements'] = data.get('requirements')
        data['is_private'] = data.get('is_private', False)
        data['security_marking'] = data.get('security_marking')

        # only checked on update, not create
        data['is_enabled'] = data.get('is_enabled', False)
        data['is_featured'] = data.get('is_featured', False)
        data['approval_status'] = data.get('approval_status')

        # Agency
        agency_title = None if data.get('agency') is None else data.get('agency', {}).get('title')
        if agency_title:
            data['agency'] = agency_model_access.get_agency_by_title(agency_title)
            if data['agency'] is None:
                raise serializers.ValidationError('Invalid Agency')
        else:
            data['agency'] = profile.organizations.all()[0]

        # Listing Type
        type_title = None if data.get('listing_type') is None else data.get('listing_type', {}).get('title')
        if type_title:
            data['listing_type'] = model_access.get_listing_type_by_title(type_title)
        else:
            data['listing_type'] = None

        # Images
        image_keys = ['small_icon', 'large_icon', 'banner_icon', 'large_banner_icon']

        for image_key in image_keys:
            current_image_value = data.get(image_key)
            if current_image_value:
                if 'id' not in current_image_value:
                    raise serializers.ValidationError('Image({!s}) requires a {!s}'.format(image_key, 'id'))
                if current_image_value.get('security_marking') is None:
                    current_image_value['security_marking'] = constants.DEFAULT_SECURITY_MARKING
                if not access_control_instance.validate_marking(current_image_value['security_marking']):
                    raise errors.InvalidInput('{!s} Security Marking is invalid'.format(image_key))
            else:
                data[image_key] = None

        # Screenshot
        screenshots = data.get('screenshots')
        if screenshots is not None:
            screenshots_out = []
            image_require_fields = ['id']
            for screenshot_set in screenshots:
                if ('small_image' not in screenshot_set or
                        'large_image' not in screenshot_set):
                    raise serializers.ValidationError(
                        'Screenshot Set requires {0!s} fields'.format('small_image, large_icon'))
                screenshot_small_image = screenshot_set.get('small_image')
                screenshot_large_image = screenshot_set.get('large_image')

                for field in image_require_fields:
                    if field not in screenshot_small_image:
                        raise serializers.ValidationError('Screenshot Small Image requires a {0!s}'.format(field))

                for field in image_require_fields:
                    if field not in screenshot_large_image:
                        raise serializers.ValidationError('Screenshot Large Image requires a {0!s}'.format(field))

                if not screenshot_small_image.get('security_marking'):
                    screenshot_small_image['security_marking'] = constants.DEFAULT_SECURITY_MARKING
                if not access_control_instance.validate_marking(screenshot_small_image['security_marking']):
                    raise errors.InvalidInput('Security Marking is invalid')

                if not screenshot_large_image.get('security_marking'):
                    screenshot_large_image['security_marking'] = constants.DEFAULT_SECURITY_MARKING
                if not access_control_instance.validate_marking(screenshot_large_image['security_marking']):
                    raise errors.InvalidInput('Security Marking is invalid')

                screenshots_out.append(screenshot_set)
                data['screenshots'] = screenshots_out
        else:
            data['screenshots'] = None

        # Contacts
        if 'contacts' in data:
            for contact in data['contacts']:
                if 'name' not in contact:
                    raise serializers.ValidationError('Contact requires [name] field')
                if 'email' not in contact:
                    raise serializers.ValidationError('Contact requires [email] field')
                if 'secure_phone' not in contact:
                    contact['secure_phone'] = None
                if 'unsecure_phone' not in contact:
                    contact['unsecure_phone'] = None
                if 'contact_type' not in contact:
                    raise serializers.ValidationError('Contact requires [contact_type] field')

                contact_type = contact.get('contact_type')
                contact_type_name = None if contact_type is None else contact_type.get('name')

                if not contact_type_name:
                    raise serializers.ValidationError('Contact field requires correct format')

                contact_type_instance = contact_type_model_access.get_contact_type_by_name(contact_type_name)
                if not contact_type_instance:
                    raise serializers.ValidationError('Contact Type [{}] not found'.format(contact_type_name))

        # owners
        owners = []
        if 'owners' in data:
            for owner in data['owners']:
                user_dict = owner.get('user')
                user_username = None if user_dict is None else user_dict.get('username')

                if not user_username:
                    raise serializers.ValidationError('Owner field requires correct format')

                owner_profile = generic_model_access.get_profile(user_username)
                if not owner_profile:
                    raise serializers.ValidationError('Owner Profile not found')

                # Don't allow user to select a security marking that is above
                # their own access level
                if not system_has_access_control(owner_profile.user.username, data.get('security_marking')):
                    raise serializers.ValidationError('Security marking too high for current owner profile')

                # Don't allow 2nd-party user to be an owner of a listing
                if system_anonymize_identifiable_data(owner_profile.user.username):
                    raise serializers.ValidationError('Permissions are invalid for current owner profile')

                owners.append(owner_profile)
        data['owners'] = owners

        # Categories
        categories = []
        if 'categories' in data:
            for category in data['categories']:
                category_title = category.get('title')
                if not category_title:
                    raise serializers.ValidationError('Categories field requires correct format')

                category_instance = category_model_access.get_category_by_title(category_title)
                if not category_instance:
                    raise serializers.ValidationError('Category [{}] not found'.format(category_title))

                categories.append(category_instance)
        data['categories'] = categories

        # Intents
        intents = []
        if 'intents' in data:
            for intent in data['intents']:
                intent_action = intent.get('action')
                if not intent_action:
                    raise serializers.ValidationError('Intent field requires correct format')

                intent_instance = intent_model_access.get_intent_by_action(intent_action)
                if not intent_instance:
                    raise serializers.ValidationError('Intent Action [{}] not found'.format(intent_action))

                intents.append(intent_instance)
        data['intents'] = intents

        # doc urls will be created in create()
        if 'doc_urls' in data:
            pass

        # tags will be created (if necessary) in create()
        if 'tags' in data:
            pass

        # logger.debug('leaving ListingSerializer.validate', extra={'request':self.context.get('request')})
        return data

    def create(self, validated_data):
        # logger.debug('inside ListingSerializer.create', extra={'request':self.context.get('request')})
        title = validated_data['title']
        user = generic_model_access.get_profile(self.context['request'].user.username)

        logger.info('creating listing {0!s} for user {1!s}'.format(title,
            user.user.username), extra={'request': self.context.get('request')})

        # TODO required_listings
        listing = models.Listing(title=title,
            agency=validated_data['agency'],
            description=validated_data['description'],
            launch_url=validated_data['launch_url'],
            version_name=validated_data['version_name'],
            unique_name=validated_data['unique_name'],
            what_is_new=validated_data['what_is_new'],
            description_short=validated_data['description_short'],
            requirements=validated_data['requirements'],
            security_marking=validated_data['security_marking'],
            listing_type=validated_data['listing_type'],
            is_private=validated_data['is_private'])

        image_keys = ['small_icon', 'large_icon', 'banner_icon', 'large_banner_icon']
        for image_key in image_keys:
            if validated_data[image_key]:
                new_value_image = image_model_access.get_image_by_id(validated_data[image_key].get('id'))

                if new_value_image is None:
                    raise errors.InvalidInput('Error while saving, can not find image by id')

                if image_key == 'small_icon':
                    listing.small_icon = new_value_image
                elif image_key == 'large_icon':
                    listing.large_icon = new_value_image
                elif image_key == 'banner_icon':
                    listing.banner_icon = new_value_image
                elif image_key == 'large_banner_icon':
                    listing.large_banner_icon = new_value_image

        listing.save()

        if validated_data.get('contacts') is not None:
            for contact in validated_data['contacts']:
                contact_type_instance = contact_type_model_access.get_contact_type_by_name(contact['contact_type']['name'])
                new_contact, created = models.Contact.objects.get_or_create(name=contact['name'],
                    email=contact['email'],
                    secure_phone=contact['secure_phone'],
                    unsecure_phone=contact['unsecure_phone'],
                    organization=contact.get('organization', None),
                    contact_type=contact_type_instance)
                new_contact.save()
                listing.contacts.add(new_contact)

        if validated_data.get('owners') is not None:
            if validated_data['owners']:
                for owner in validated_data['owners']:
                    listing.owners.add(owner)
            else:
                # if no owners are specified, just add the current user
                listing.owners.add(user)

        if validated_data.get('categories') is not None:
            for category in validated_data['categories']:
                listing.categories.add(category)

        # tags will be automatically created if necessary
        if validated_data.get('tags') is not None:
            for tag in validated_data['tags']:
                obj, created = models.Tag.objects.get_or_create(
                    name=tag['name'])
                listing.tags.add(obj)

        if validated_data.get('intents') is not None:
            for intent in validated_data['intents']:
                listing.intents.add(intent)

        # doc_urls will be automatically created
        if validated_data.get('doc_urls') is not None:
            for d in validated_data['doc_urls']:
                doc_url = models.DocUrl(name=d['name'], url=d['url'], listing=listing)
                doc_url.save()

        # screenshots will be automatically created
        if validated_data.get('screenshots') is not None:
            for screenshot_dict in validated_data['screenshots']:
                screenshot = models.Screenshot(
                    small_image=image_model_access.get_image_by_id(screenshot_dict['small_image']['id']),
                    large_image=image_model_access.get_image_by_id(screenshot_dict['large_image']['id']),
                    listing=listing)
                screenshot.save()

        # create a new activity
        model_access.create_listing(user, listing)

        dispatcher.publish('listing_created', listing=listing, profile=user)
        return listing

    def update(self, instance, validated_data):
        # logger.debug('inside ListingSerializer.update', extra={'request':self.context.get('request')})
        user = generic_model_access.get_profile(
            self.context['request'].user.username)

        if user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            if user not in instance.owners.all():
                raise errors.PermissionDenied(
                    'User ({0!s}) is not an owner of this listing'.format(user.username))

        if instance.is_deleted:
            raise errors.PermissionDenied('Cannot update a previously deleted listing')

        change_details = []

        simple_fields = ['title', 'description', 'description_short',
            'launch_url', 'version_name', 'requirements', 'unique_name',
            'what_is_new', 'security_marking']

        for i in simple_fields:
            if getattr(instance, i) != validated_data[i]:
                change_details.append({'old_value': getattr(instance, i),
                    'new_value': validated_data[i], 'field_name': i})
                setattr(instance, i, validated_data[i])

        if validated_data['is_enabled'] != instance.is_enabled:
            if validated_data['is_enabled']:
                model_access.enable_listing(user, instance)
            else:
                model_access.disable_listing(user, instance)

            instance.is_enabled = validated_data['is_enabled']

            if validated_data['approval_status'] == models.Listing.APPROVED:
                dispatcher.publish('listing_enabled_status_changed',
                                   listing=instance,
                                   profile=user,
                                   is_enabled=validated_data['is_enabled'])

        if validated_data['is_private'] != instance.is_private:
            changeset = {'old_value': model_access.bool_to_string(instance.is_private),
                    'new_value': model_access.bool_to_string(validated_data['is_private']), 'field_name': 'is_private'}
            change_details.append(changeset)
            instance.is_private = validated_data['is_private']

            if validated_data['approval_status'] == models.Listing.APPROVED:
                dispatcher.publish('listing_private_status_changed',
                                   listing=instance,
                                   profile=user,
                                   is_private=validated_data['is_private'])

        if validated_data['is_featured'] != instance.is_featured:
            if user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
                raise errors.PermissionDenied('Only stewards can change is_featured setting of a listing')
            change_details.append({'old_value': model_access.bool_to_string(instance.is_featured),
                    'new_value': model_access.bool_to_string(validated_data['is_featured']), 'field_name': 'is_featured'})
            instance.is_featured = validated_data['is_featured']

        s = validated_data['approval_status']
        if s and s != instance.approval_status:  # Check to see if approval_status has changed
            if s == models.Listing.APPROVED and user.highest_role() != 'APPS_MALL_STEWARD':
                raise errors.PermissionDenied('Only an APPS_MALL_STEWARD can mark a listing as APPROVED')
            if s == models.Listing.APPROVED_ORG and user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
                raise errors.PermissionDenied('Only stewards can mark a listing as APPROVED_ORG')
            if s == models.Listing.PENDING:
                model_access.submit_listing(user, instance)
            if s == models.Listing.PENDING_DELETION:
                model_access.pending_delete_listing(user, instance)
            if s == models.Listing.APPROVED_ORG:
                model_access.approve_listing_by_org_steward(user, instance)
            if s == models.Listing.APPROVED:
                model_access.approve_listing(user, instance)
            if s == models.Listing.REJECTED:
                # TODO: need to get the rejection text from somewhere
                model_access.reject_listing(user, instance, 'TODO: rejection reason')

            dispatcher.publish('listing_approval_status_change',
                               listing=instance,
                               profile=user,
                               approval_status=instance.approval_status)

        if instance.listing_type != validated_data['listing_type']:
            if instance.listing_type:
                old_value = instance.listing_type.title
            else:
                old_value = None
            if validated_data['listing_type']:
                new_value = validated_data['listing_type'].title
            else:
                new_value = None
            change_details.append({'old_value': old_value,
                    'new_value': new_value, 'field_name': 'listing_type'})
            instance.listing_type = validated_data['listing_type']

        image_keys = ['small_icon', 'large_icon', 'banner_icon', 'large_banner_icon']
        for image_key in image_keys:
            if validated_data[image_key]:
                old_value = model_access.image_to_string(getattr(instance, image_key), True, 'old_value({0!s})'.format(image_key))
                new_value = model_access.image_to_string(validated_data[image_key], False, 'new_value({0!s})'.format(image_key))

                if old_value != new_value:
                    new_value_image = None

                    old_image_id = None
                    if old_value is not None:
                        old_image_id = getattr(instance, image_key).id
                    if validated_data[image_key].get('id') == old_image_id:
                        new_value_image = getattr(instance, image_key)
                        new_value_image.security_marking = validated_data[image_key].get('security_marking')
                        new_value_image.save()
                    else:
                        new_value_image = image_model_access.get_image_by_id(validated_data[image_key].get('id'))

                        if new_value_image is None:
                            raise errors.InvalidInput('Error while saving, can not find image by id')

                    change_details.append({'old_value': old_value,
                            'new_value': new_value, 'field_name': image_key})

                    if image_key == 'small_icon':
                        instance.small_icon = new_value_image
                    elif image_key == 'large_icon':
                        instance.large_icon = new_value_image
                    elif image_key == 'banner_icon':
                        instance.banner_icon = new_value_image
                    elif image_key == 'large_banner_icon':
                        instance.large_banner_icon = new_value_image

        if 'contacts' in validated_data:
            old_contact_instances = instance.contacts.all()
            old_contacts = model_access.contacts_to_string(old_contact_instances, True)
            new_contacts = model_access.contacts_to_string(validated_data['contacts'])

            if old_contacts != new_contacts:
                change_details.append({'old_value': old_contacts,
                    'new_value': new_contacts, 'field_name': 'contacts'})
                instance.contacts.clear()
                for contact in validated_data['contacts']:
                    # TODO: Smarter Handling of Duplicates Contact Records
                    # A contact with the same name and email should be the same contact
                    # in the backend.
                    # Person1(name='N1',email='n2@n2.com') and
                    #    Person1' (name='N1',email='n2@n2.com',secure_phone = '414-444-444')
                    # The two people above should be one contact
                    # if approval_status: "IN_PROGRESS" then it should be using
                    # contact model ids' since it is temporary contacts
                    obj, created = models.Contact.objects.get_or_create(
                        name=contact['name'],
                        email=contact['email'],
                        secure_phone=contact['secure_phone'],
                        unsecure_phone=contact['unsecure_phone'],
                        organization=contact.get('organization', None),
                        contact_type=contact_type_model_access.get_contact_type_by_name(
                            contact['contact_type']['name'])
                    )
                    instance.contacts.add(obj)

        if 'categories' in validated_data:
            old_category_instances = instance.categories.all()
            old_categories = model_access.categories_to_string(old_category_instances, True)
            new_categories = model_access.categories_to_string(validated_data['categories'], True)

            if old_categories != new_categories:
                changeset = {'old_value': old_categories,
                    'new_value': new_categories, 'field_name': 'categories'}
                change_details.append(changeset)
                instance.categories.clear()
                for category in validated_data['categories']:
                    instance.categories.add(category)

                if validated_data['approval_status'] == models.Listing.APPROVED:
                    dispatcher.publish('listing_categories_changed',
                                       listing=instance,
                                       profile=user,
                                       old_categories=old_category_instances,
                                       new_categories=validated_data['categories'])

        if 'owners' in validated_data:
            old_owner_instances = instance.owners.all()
            old_owners = model_access.owners_to_string(old_owner_instances, True)
            new_owners = model_access.owners_to_string(validated_data['owners'], True)
            if old_owners != new_owners:
                change_details.append({'old_value': old_owners,
                    'new_value': new_owners, 'field_name': 'owners'})
                instance.owners.clear()
                for owner in validated_data['owners']:
                    instance.owners.add(owner)

        # tags will be automatically created if necessary
        if 'tags' in validated_data:
            old_tag_instances = instance.tags.all()
            old_tags = model_access.tags_to_string(old_tag_instances, True)
            new_tags = model_access.tags_to_string(validated_data['tags'])

            if old_tags != new_tags:
                changeset = {'old_value': old_tags,
                             'new_value': new_tags, 'field_name': 'tags'}
                change_details.append(changeset)
                instance.tags.clear()
                new_tags_instances = []
                for tag in validated_data['tags']:
                    obj, created = models.Tag.objects.get_or_create(
                        name=tag['name'])
                    instance.tags.add(obj)
                    new_tags_instances.append(obj)

                if validated_data['approval_status'] == models.Listing.APPROVED:
                    dispatcher.publish('listing_tags_changed',
                                       listing=instance,
                                       profile=user,
                                       old_tags=old_tag_instances,
                                       new_tags=new_tags_instances)

        if 'intents' in validated_data:
            old_intent_instances = instance.intents.all()
            old_intents = model_access.intents_to_string(old_intent_instances, True)
            new_intents = model_access.intents_to_string(validated_data['intents'], True)
            if old_intents != new_intents:
                change_details.append({'old_value': old_intents,
                    'new_value': new_intents, 'field_name': 'intents'})
                instance.intents.clear()
                for intent in validated_data['intents']:
                    instance.intents.add(intent)

        # doc_urls will be automatically created
        if 'doc_urls' in validated_data:
            old_doc_url_instances = model_access.get_doc_urls_for_listing(instance)
            old_doc_urls = model_access.doc_urls_to_string(old_doc_url_instances, True)
            new_doc_urls = model_access.doc_urls_to_string(validated_data['doc_urls'])
            if old_doc_urls != new_doc_urls:
                change_details.append({
                    'old_value': old_doc_urls,
                    'new_value': new_doc_urls,
                    'field_name': 'doc_urls'})

                new_doc_url_instances = []
                for d in validated_data['doc_urls']:
                    obj, created = models.DocUrl.objects.get_or_create(
                        name=d['name'], url=d['url'], listing=instance)
                    new_doc_url_instances.append(obj)
                for i in old_doc_url_instances:
                    if i not in new_doc_url_instances:
                        logger.info('Deleting doc_url: {0!s}'.format(i.id), extra={'request': self.context.get('request')})
                        i.delete()

        # screenshots will be automatically created
        if 'screenshots' in validated_data:
            old_screenshot_instances = model_access.get_screenshots_for_listing(instance)
            old_screenshots = model_access.screenshots_to_string(old_screenshot_instances, True)
            new_screenshots = model_access.screenshots_to_string(validated_data['screenshots'])
            if old_screenshots != new_screenshots:
                change_details.append({'old_value': old_screenshots,
                    'new_value': new_screenshots, 'field_name': 'screenshots'})

            new_screenshot_instances = []

            for s in validated_data['screenshots']:
                new_small_image = image_model_access.get_image_by_id(s['small_image']['id'])
                new_small_image.security_marking = s['small_image']['security_marking']
                new_small_image.save()

                new_large_image = image_model_access.get_image_by_id(s['large_image']['id'])
                new_large_image.security_marking = s['large_image']['security_marking']
                new_large_image.save()

                obj, created = models.Screenshot.objects.get_or_create(
                    small_image=new_small_image,
                    large_image=new_large_image,
                    listing=instance)

                new_screenshot_instances.append(obj)

            for i in old_screenshot_instances:
                if i not in new_screenshot_instances:
                    logger.info('Deleting screenshot: {0!s}'.format(i.id), extra={'request': self.context.get('request')})
                    i.delete()

        if 'agency' in validated_data:
            if instance.agency != validated_data['agency']:
                change_details.append({'old_value': instance.agency.title,
                    'new_value': validated_data['agency'].title, 'field_name': 'agency'})
                instance.agency = validated_data['agency']

        instance.save()

        # If the listing was modified add an entry showing changes
        if change_details:
            model_access.log_listing_modification(user, instance, change_details)

        instance.edited_date = datetime.datetime.now(pytz.utc)
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()

    class Meta:
        model = models.Review
        fields = ('author', 'listing', 'rate', 'text', 'edited_date', 'id')
