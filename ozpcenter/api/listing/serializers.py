"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import ozpcenter.models as models
import ozpcenter.constants as constants

import ozpcenter.api.listing.model_access as model_access
import ozpcenter.api.profile.serializers as profile_serializers
import ozpcenter.api.agency.serializers as agency_serializers
import ozpcenter.model_access as generic_model_access
import ozpcenter.errors as errors

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AccessControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccessControl
        fields = ('title',)

        extra_kwargs = {
            'title': {'validators': []}
        }

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    access_control = AccessControlSerializer(required=False)
    class Meta:
        model = models.Image
        fields = ('url', 'id', 'access_control')

        extra_kwargs = {
            'access_control': {'validators': []},
            "id": {
                "read_only": False,
                "required": False,
            }
        }


class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactType
        fields = ('name',)

        extra_kwargs = {
            'name': {'validators': []}
        }

# contacts are only used in conjunction with Listings
class ContactSerializer(serializers.ModelSerializer):
    contact_type = ContactTypeSerializer()
    class Meta:
        model = models.Contact

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


# class RejectionListingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.RejectionListing


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


class ListingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListingActivity
        fields = ('action',)

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
        model = django.contrib.auth.models.User
        fields = ('username',)

        extra_kwargs = {
            'username': {'validators': []}
        }


class CreateListingProfileSerializer(serializers.ModelSerializer):
    user = CreateListingUserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user', 'display_name', 'id')
        read_only = ('display_name', 'id')


class ListingSerializer(serializers.ModelSerializer):
    screenshots = ScreenshotSerializer(many=True, required=False)
    doc_urls  = DocUrlSerializer(many=True, required=False)
    owners = CreateListingProfileSerializer(required=False, many=True)
    categories = CategorySerializer(many=True,
        required=False)
    tags = TagSerializer(many=True, required=False)
    contacts = ContactSerializer(many=True, required=False)
    intents = IntentSerializer(many=True, required=False)
    access_control = AccessControlSerializer(required=False)
    small_icon = ImageSerializer(required=False, allow_null=True)
    large_icon = ImageSerializer(required=False, allow_null=True)
    banner_icon = ImageSerializer(required=False, allow_null=True)
    large_banner_icon = ImageSerializer(required=False, allow_null=True)
    agency = agency_serializers.AgencySerializer(required=False, read_only=True)
    last_activity = ListingActivitySerializer(required=False, read_only=True)
    listing_type = ListingTypeSerializer(required=False, allow_null=True)

    class Meta:
        model = models.Listing
        depth = 2

    def validate(self, data):
        logger.debug('inside ListingSerializer.validate')
        if 'title' not in data:
            raise serializers.ValidationError('Title is required')

        data['description'] = data.get('description', None)
        data['launch_url'] = data.get('launch_url', None)
        data['version_name'] = data.get('version_name', None)
        data['unique_name'] = data.get('unique_name', None)
        data['what_is_new'] = data.get('what_is_new', None)
        data['description_short'] = data.get('description_short', None)
        data['requirements'] = data.get('requirements', None)
        data['is_private'] = data.get('is_private', False)

        # only checked on update, not create
        data['is_enabled'] = data.get('is_enabled', False)
        data['is_featured'] = data.get('is_featured', False)
        data['approval_status'] = data.get('approval_status', None)

        # acces_control
        access_control_title = data.get('access_control', None)
        if access_control_title:
            data['access_control'] = models.AccessControl.objects.get(
                title=data['access_control']['title'])
        else:
            data['access_control'] = None

        # listing_type
        type_title = data.get('listing_type', None)
        if type_title:
            data['listing_type'] = models.ListingType.objects.get(
                title=data['listing_type']['title'])
        else:
            data['listing_type'] = None

        # small_icon
        small_icon = data.get('small_icon', None)
        if small_icon:
            data['small_icon'] = models.Image.objects.get(
                id=data['small_icon']['id'])
        else:
            data['small_icon'] = None

        # large_icon
        large_icon = data.get('large_icon', None)
        if large_icon:
            data['large_icon'] = models.Image.objects.get(
                id=data['large_icon']['id'])
        else:
            data['large_icon'] = None

        # banner_icon
        banner_icon = data.get('banner_icon', None)
        if banner_icon:
            data['banner_icon'] = models.Image.objects.get(
                id=data['banner_icon']['id'])
        else:
            data['banner_icon'] = None

        # large_banner_icon
        large_banner_icon = data.get('large_banner_icon', None)
        if large_banner_icon:
            data['large_banner_icon'] = models.Image.objects.get(
                id=data['large_banner_icon']['id'])
        else:
            data['large_banner_icon'] = None

        if 'contacts' in data:
            required_fields = ['email', 'secure_phone', 'unsecure_phone',
            'name', 'contact_type']
            for contact in data['contacts']:
                for field in required_fields:
                    if field not in contact:
                        raise serializers.ValidationError(
                            'Contact requires a %s' % field)


        owners = []
        if 'owners' in data:
            for owner in data['owners']:
                owners.append(models.Profile.objects.get(
                    user__username=owner['user']['username']))
        data['owners'] = owners

        categories = []
        if 'categories' in data:
            for category in data['categories']:
                categories.append(models.Category.objects.get(
                    title=category['title']))
        data['categories'] = categories

        # tags will be created (if necessary) in create()
        if 'tags' in data:
            pass

        intents = []
        if 'intents' in data:
            for intent in data['intents']:
                intents.append(models.Intent.objects.get(
                    action=intent['action']))
        data['intents'] = intents

        # doc urls will be created in create()
        if 'doc_urls' in data:
            pass

        # screenshots will be created in create()
        if 'screenshots' in data:
            pass

        return data

    def create(self, validated_data):
        title = validated_data['title']
        user = generic_model_access.get_profile(
            self.context['request'].user.username)
        logger.info('creating listing %s for user %s' % (title,
            user.user.username))
        # TODO: what to use if user belongs to multiple agencies?
        agency = user.organizations.all()[0]

        # assign a default access_control level if none is provided
        if not validated_data['access_control']:
            validated_data['access_control'] = models.AccessControl.objects.get(
                title=constants.DEFAULT_ACCESS_CONTROL)

        # TODO required_listings
        listing = models.Listing(title=title, agency=agency,
            description=validated_data['description'],
            launch_url=validated_data['launch_url'],
            version_name=validated_data['version_name'],
            unique_name=validated_data['unique_name'],
            what_is_new=validated_data['what_is_new'],
            description_short=validated_data['description_short'],
            requirements=validated_data['requirements'],
            access_control=validated_data['access_control'],
            listing_type=validated_data['listing_type'],
            small_icon=validated_data['small_icon'],
            large_icon=validated_data['large_icon'],
            banner_icon=validated_data['banner_icon'],
            large_banner_icon=validated_data['large_banner_icon'],
            is_private=validated_data['is_private'])

        listing.save()

        if 'contacts' in validated_data:
            for contact in validated_data['contacts']:
                new_contact = models.Contact(name=contact['name'],
                    email=contact['email'],
                    secure_phone=contact['secure_phone'],
                    unsecure_phone=contact['unsecure_phone'],
                    organization=contact.get('organization', None),
                    contact_type=models.ContactType.objects.get(
                        name=contact['contact_type']['name']))
                new_contact.save()
                listing.contacts.add(new_contact)

        if 'owners' in validated_data:
            if validated_data['owners']:
                for owner in validated_data['owners']:
                    listing.owners.add(owner)
            else:
                # if no owners are specified, just add the current user
                listing.owners.add(user)

        if 'categories' in validated_data:
            for category in validated_data['categories']:
                listing.categories.add(category)

        # tags will be automatically created if necessary
        if 'tags' in validated_data:
            for tag in validated_data['tags']:
                obj, created = models.Tag.objects.get_or_create(
                    name=tag['name'])
                listing.tags.add(obj)

        if 'intents' in validated_data:
            for intent in validated_data['intents']:
                listing.intents.add(intent)

        # doc_urls will be automatically created
        if 'doc_urls' in validated_data:
            for d in validated_data['doc_urls']:
                doc_url = models.DocUrl(name=d['name'], url=d['url'], listing=listing)
                doc_url.save()

        # screenshots will be automatically created
        if 'screenshots' in validated_data:
            for s in validated_data['screenshots']:
                screenshot = models.Screenshot(
                    small_image=models.Image.objects.get(id=s['small_image']['id']),
                    large_image=models.Image.objects.get(id=s['large_image']['id']),
                    listing=listing)
                screenshot.save()

        # create a new activity
        model_access.create_listing(user, listing)

        return listing

    def update(self, instance, validated_data):
        user = generic_model_access.get_profile(
            self.context['request'].user.username)

        if user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
            if user not in instance.owners.all():
                raise errors.PermissionDenied(
                    'User is not an owner of this listing')

        change_details = []

        simple_fields = ['title', 'description', 'description_short',
            'launch_url', 'version_name', 'requirements', 'unique_name',
            'what_is_new']

        for i in simple_fields:
            if getattr(instance, i) != validated_data[i]:
                change_details.append({'old_value': getattr(instance, i),
                    'new_value': validated_data[i], 'field_name': i})
                setattr(instance, i, validated_data[i])

        if validated_data['is_enabled'] != instance.is_enabled:
            change_details.append({'old_value':model_access.bool_to_string(instance.is_enabled),
                    'new_value': model_access.bool_to_string(validated_data['is_enabled']), 'field_name': 'is_enabled'})
            instance.is_enabled = validated_data['is_enabled']

        if validated_data['is_private'] != instance.is_private:
            change_details.append({'old_value': model_access.bool_to_string(instance.is_private),
                    'new_value': model_access.bool_to_string(validated_data['is_private']), 'field_name': 'is_private'})
            instance.is_private = validated_data['is_private']

        if validated_data['is_featured'] != instance.is_featured:
            if user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
                raise errors.PermissionDenied('Only stewards can change is_featured setting of a listing')
            change_details.append({'old_value': model_access.bool_to_string(instance.is_featured),
                    'new_value': model_access.bool_to_string(validated_data['is_featured']), 'field_name': 'is_featured'})
            instance.is_featured = validated_data['is_featured']

        s = validated_data['approval_status']
        if s and s != instance.approval_status:
            if s == models.ApprovalStatus.APPROVED and user.highest_role() != 'APPS_MALL_STEWARD':
                raise errors.PermissionDenied('Only an APPS_MALL_STEWARD can mark a listing as APPROVED')
            if s == models.ApprovalStatus.APPROVED_ORG and user.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
                raise errors.PermissionDenied('Only stewards can mark a listing as APPROVED_ORG')

            if s == models.ApprovalStatus.PENDING:
                # user has submitted this app
                model_access.submit_listing(user, instance)

            change_details.append({'old_value': instance.approval_status,
                    'new_value': validated_data['approval_status'], 'field_name': 'approval_status'})
            instance.approval_status = validated_data['approval_status']

        if instance.access_control != validated_data['access_control']:
            change_details.append({'old_value': instance.access_control.title,
                    'new_value': validated_data['access_control'].title, 'field_name': 'access_control'})
            instance.access_control = validated_data['access_control']

        if instance.listing_type != validated_data['listing_type']:
            change_details.append({'old_value': instance.listing_type.title,
                    'new_value': validated_data['listing_type'].title, 'field_name': 'listing_type'})
            instance.listing_type = validated_data['listing_type']

        if instance.small_icon != validated_data['small_icon']:
            change_details.append({'old_value': instance.small_icon.id,
                    'new_value': validated_data['small_icon'].id, 'field_name': 'small_icon'})
            instance.small_icon = validated_data['small_icon']

        if instance.large_icon != validated_data['large_icon']:
            change_details.append({'old_value': instance.large_icon.id,
                    'new_value': validated_data['large_icon'].id, 'field_name': 'large_icon'})
            instance.large_icon = validated_data['large_icon']

        if instance.banner_icon != validated_data['banner_icon']:
            change_details.append({'old_value': instance.banner_icon.id,
                    'new_value': validated_data['banner_icon'].id, 'field_name': 'banner_icon'})
            instance.banner_icon = validated_data['banner_icon']

        if instance.large_banner_icon != validated_data['large_banner_icon']:
            change_details.append({'old_value': instance.large_banner_icon.id,
                    'new_value': validated_data['large_banner_icon'].id, 'field_name': 'large_banner_icon'})
            instance.large_banner_icon = validated_data['large_banner_icon']

        if 'contacts' in validated_data:
            old_contact_instances = instance.contacts.all()
            old_contacts = model_access.contacts_to_string(
                old_contact_instances, True)
            new_contacts = model_access.contacts_to_string(
                validated_data['contacts'])
            if old_contacts != new_contacts:
                change_details.append({'old_value': old_contacts,
                    'new_value': new_contacts, 'field_name': 'contacts'})
                instance.contacts.clear()
                for contact in validated_data['contacts']:
                    obj, created = models.Contact.objects.get_or_create(
                        name=contact['name'],
                        email=contact['email'],
                        secure_phone=contact['secure_phone'],
                        unsecure_phone=contact['unsecure_phone'],
                        organization=contact.get('organization', None),
                        contact_type=models.ContactType.objects.get(
                            name=contact['contact_type']['name'])
                    )
                    instance.contacts.add(obj)

        if 'categories' in validated_data:
            old_category_instances = instance.categories.all()
            old_categories = model_access.categories_to_string(
                old_category_instances, True)
            new_categories = model_access.categories_to_string(
                validated_data['categories'], True)
            if old_categories != new_categories:
                change_details.append({'old_value': old_categories,
                    'new_value': new_categories, 'field_name': 'categories'})
                instance.categories.clear()
                for category in validated_data['categories']:
                    instance.categories.add(category)

        if 'owners' in validated_data:
            old_owner_instances = instance.owners.all()
            old_owners = model_access.owners_to_string(
                old_owner_instances, True)
            new_owners = model_access.owners_to_string(
                validated_data['owners'], True)
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
                change_details.append({'old_value': old_tags,
                    'new_value': new_tags, 'field_name': 'tags'})
                instance.tags.clear()
                for tag in validated_data['tags']:
                    obj, created = models.Tag.objects.get_or_create(
                        name=tag['name'])
                    instance.tags.add(obj)

        if 'intents' in validated_data:
            old_intent_instances = instance.intents.all()
            old_intents = model_access.intents_to_string(old_intent_instances,
                True)
            new_intents = model_access.intents_to_string(
                validated_data['intents'], True)
            if old_intents != new_intents:
                change_details.append({'old_value': old_intents,
                    'new_value': new_intents, 'field_name': 'intents'})
                instance.intents.clear()
                for intent in validated_data['intents']:
                    instance.intents.add(intent)

        # doc_urls will be automatically created
        if 'doc_urls' in validated_data:
            old_doc_url_instances = models.DocUrl.objects.filter(
                listing=instance)
            old_doc_urls = model_access.doc_urls_to_string(
                old_doc_url_instances, True)
            new_doc_urls = model_access.doc_urls_to_string(
                validated_data['doc_urls'])
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
                        logger.info('Deleting doc_url: %s' % i.id)
                        i.delete()

        # screenshots will be automatically created
        if 'screenshots' in validated_data:
            old_screenshot_instances = models.Screenshot.objects.filter(
                listing=instance)
            old_screenshots = model_access.screenshots_to_string(old_screenshot_instances, True)
            new_screenshots = model_access.screenshots_to_string(
                validated_data['screenshots'])
            if old_screenshots != new_screenshots:
                change_details.append({'old_value': old_screenshots,
                    'new_value': new_screenshots, 'field_name': 'screenshots'})

            new_screenshot_instances = []
            for s in validated_data['screenshots']:
                obj, created = models.Screenshot.objects.get_or_create(
                    small_image=models.Image.objects.get(
                        id=s['small_image']['id']),
                    large_image=models.Image.objects.get(
                        id=s['large_image']['id']),
                    listing=instance)
                new_screenshot_instances.append(obj)
            for i in old_screenshot_instances:
                if i not in new_screenshot_instances:
                    logger.info('Deleting screenshot: %s' % i.id)
                    i.delete()

        # TODO: allow agency change?
        instance.save()

        model_access.log_listing_modification(user, instance, change_details)
        return instance


class ItemCommentSerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()
    class Meta:
        model = models.ItemComment
        fields = ('author', 'listing', 'rate', 'text', 'id')


class ShortListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('unique_name', 'title')


class ListingActivitySerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()
    listing = ShortListingSerializer()
    change_details = ChangeDetailSerializer(many=True)
    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date', 'description', 'author', 'listing',
            'change_details')