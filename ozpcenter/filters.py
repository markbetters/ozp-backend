"""
filters
"""
import django_filters
import ozpcenter.models as models

class ProfileFilter(django_filters.FilterSet):
	class Meta:
		model = models.Profile
		fields = ['highest_role']

class ListingFilter(django_filters.FilterSet):
    class Meta:
        model = models.Listing