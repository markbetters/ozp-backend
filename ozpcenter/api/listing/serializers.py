"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import ozpcenter.models as models

import ozpcenter.api.profile.serializers as profile_serializers
import ozpcenter.api.agency.serializers as agency_serializers
import ozpcenter.model_access as generic_model_access

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
    small_icon = ImageSerializer(required=False)
    large_icon = ImageSerializer(required=False)
    banner_icon = ImageSerializer(required=False)
    large_banner_icon = ImageSerializer(required=False)
    agency = agency_serializers.AgencySerializer(required=False, read_only=True)
    last_activity = ListingActivitySerializer(required=False, read_only=True)
    listing_type = ListingTypeSerializer(required=False)

    class Meta:
        model = models.Listing
        depth = 2

    def validate(self, data):
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
            for owner in validated_data['owners']:
                listing.owners.add(owner)

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

        return listing

    def update(self, instance, validated_data):
        instance.title = validated_data['title']
        instance.description = validated_data['description']
        instance.description_short = validated_data['description_short']
        instance.launch_url = validated_data['launch_url']
        instance.version_name = validated_data['version_name']
        instance.requirements = validated_data['requirements']
        instance.unique_name = validated_data['unique_name']
        instance.what_is_new = validated_data['what_is_new']
        instance.is_private = validated_data['is_private']
        # TODO: permission check
        instance.is_enabled = validated_data['is_enabled']
        # TODO: permission check
        instance.is_featured = validated_data['is_featured']

        instance.access_control = validated_data['access_control']
        instance.listing_type = validated_data['listing_type']
        instance.small_icon = validated_data['small_icon']
        instance.large_icon = validated_data['large_icon']
        instance.banner_icon = validated_data['banner_icon']
        instance.large_banner_icon = validated_data['large_banner_icon']

        if 'contacts' in validated_data:
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
            instance.categories.clear()
            for category in validated_data['categories']:
                instance.categories.add(category)

        if 'owners' in validated_data:
            instance.owners.clear()
            for owner in validated_data['owners']:
                instance.owners.add(owner)

        # tags will be automatically created if necessary
        if 'tags' in validated_data:
            instance.tags.clear()
            for tag in validated_data['tags']:
                obj, created = models.Tag.objects.get_or_create(
                    name=tag['name'])
                instance.tags.add(obj)

        # TODO: allow agency change?



        instance.save()

        # special fields:

        # approval_status
        # is_enabled
        # is_featured
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