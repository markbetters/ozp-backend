"""
Storefront and Metadata Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.api.listing.serializers as listing_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class StorefrontSerializer(serializers.Serializer):
    featured = listing_serializers.ListingSerializer(many=True)
    recent = listing_serializers.ListingSerializer(many=True)
    most_popular = listing_serializers.ListingSerializer(many=True)
