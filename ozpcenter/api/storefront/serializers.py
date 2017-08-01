"""
Storefront Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.api.listing.serializers as listing_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class StorefrontSerializer(serializers.Serializer):
    recommended = listing_serializers.StorefrontListingSerializer(many=True)
    featured = listing_serializers.StorefrontListingSerializer(many=True)
    recent = listing_serializers.StorefrontListingSerializer(many=True)
    most_popular = listing_serializers.StorefrontListingSerializer(many=True)
