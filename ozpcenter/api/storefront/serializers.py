"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.listing.serializers as listing_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class StorefrontSerializer(serializers.Serializer):
    featured = listing_serializers.ListingSerializer(many=True)
    recent = listing_serializers.ListingSerializer(many=True)
    most_popular = listing_serializers.ListingSerializer(many=True)