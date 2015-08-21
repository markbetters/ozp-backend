"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers

import ozpcenter.models as models

import ozpcenter.api.image.serializers as image_serializers
import ozpcenter.api.category.serializers as category_serializers
import ozpcenter.api.profile.serializers as profile_serializers
import ozpcenter.api.intent.serializers as intent_serializers
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

class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactType
        fields = ('name',)

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


# class RejectionListingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.RejectionListing


class ScreenshotSerializer(serializers.ModelSerializer):
    small_image = image_serializers.ImageSerializer()
    large_image = image_serializers.ImageSerializer()
    class Meta:
        model = models.Screenshot
        fields = ('small_image', 'large_image')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag


class ChangeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChangeDetail

class ListingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListingActivity
        fields = ('action',)


# class CreateListingUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = django.contrib.auth.models.User
#         fields = ('username',)


class CreateListingProfileSerializer(serializers.ModelSerializer):
    user = profile_serializers.ShortUserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user', 'display_name', 'id')
        read_only = ('display_name', 'id')


class ListingSerializer(serializers.ModelSerializer):
    screenshots = ScreenshotSerializer(many=True, required=False)
    doc_urls  = DocUrlSerializer(many=True, required=False)
    owners = CreateListingProfileSerializer(required=False, many=True)
    # owners = serializers.SlugRelatedField(
    #     slug_field='username',
    #     queryset=django.contrib.auth.models.User.objects.all(),
    #     many=True
    # )
    categories  = category_serializers.CategorySerializer(many=True,
        required=False)
    tags = TagSerializer(many=True, required=False)
    contacts = ContactSerializer(many=True, required=False)
    intents = intent_serializers.IntentSerializer(many=True, required=False)
    # access_control = serializers.SlugRelatedField(
    #     slug_field='title',
    #     source='*',
    #     queryset=models.AccessControl.objects.all(),
    #     required=False
    # )
    access_control = AccessControlSerializer(required=False)
    small_icon = image_serializers.ImageSerializer(required=False)
    large_icon = image_serializers.ImageSerializer(required=False)
    banner_icon = image_serializers.ImageSerializer(required=False)
    large_banner_icon = image_serializers.ImageSerializer(required=False)
    agency = agency_serializers.AgencySerializer(required=False, read_only=True)
    last_activity = ListingActivitySerializer(required=False, read_only=True)
    listing_type = ListingTypeSerializer(required=False)

    class Meta:
        model = models.Listing
        depth = 2

    def validate(self, data):
        logger.info('inside ListingSerializer validate')
        if 'title' not in data:
            raise serializers.ValidationError('Title is required')

        data['description'] = data.get('description', None)
        data['launch_url'] = data.get('launch_url', None)
        data['version_name'] = data.get('version_name', None)
        data['unique_name'] = data.get('unique_name', None)
        data['what_is_new'] = data.get('what_is_new', None)
        data['description_short'] = data.get('description_short', None)
        data['requirements'] = data.get('requirements', None)

        # acces_control
        access_control_title = data.get('access_control', None)
        if access_control_title:
            data['access_control'] = models.AccessControl.objects.get(
                title=data['access_control']['title'])
        else:
            data['access_control'] = None

        # type
        type_title = data.get('listing_type', None)
        if type_title:
            data['listing_type'] = models.ListingType.objects.get(
                title=data['listing_type']['title'])
        else:
            data['listing_type'] = None

        # small_icon

        # large_icon

        # banner_icon

        # large_banner_icon

        if 'contacts' in data:
            required_fields = ['email', 'secure_phone', 'unsecure_phone',
            'name', 'contact_type']
            for contact in data['contacts']:
                for field in required_fields:
                    if field not in contact:
                        raise serializers.ValidationError(
                            'Contact requires a %s' % field)

        # if 'owners' in data:
        #     required_fields = ['user']
        #     for owner in data['owners']:
        #         for field in required_fields:
        #             if field not in contact:
        #                 raise serializers.ValidationError(
        #                     'Owner requires a %s' % field)

        if 'categories' in data:
            pass

        if 'tags' in data:
            pass

        if 'intents' in data:
            pass

        if 'tags' in data:
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

        # access_control

        # type

        # small_icon

        # large_icon

        # banner_icon

        # large_banner_icon

        # required_listings

        listing = models.Listing(title=title, agency=agency,
            description=validated_data['description'],
            launch_url=validated_data['launch_url'],
            version_name=validated_data['version_name'],
            unique_name=validated_data['unique_name'],
            what_is_new=validated_data['what_is_new'],
            description_short=validated_data['description_short'],
            requirements=validated_data['requirements'],
            access_control=validated_data['access_control'],
            listing_type=validated_data['listing_type'])

        listing.save()

        if 'contacts' in validated_data:
            for contact in validated_data['contacts']:
                new_contact = models.Contact(name=contact['name'],
                    email=contact['email'],
                    secure_phone=contact['secure_phone'],
                    unsecure_phone=contact['unsecure_phone'],
                    organization=contact.get('organization', None),
                    contact_type=contact['contact_type'])
                new_contact.save()
                listing.contacts.add(new_contact)

        if 'owners' in validated_data:
            logger.debug('owners: %s' % validated_data['owners'])
            for owner in validated_data['owners']:
                print ('adding owner: %s' % owner)
                listing.owners.add(owner)

        if 'categories' in validated_data:
            pass

        if 'tags' in validated_data:
            pass

        if 'intents' in validated_data:
            pass

        if 'tags' in validated_data:
            pass


        return listing

    def update(self, instance, validated_data):
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