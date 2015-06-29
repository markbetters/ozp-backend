"""
filters
"""
import django_filters
import ozpcenter.models as models

class ProfileFilter(django_filters.FilterSet):
	class Meta:
		model = models.Profile
		fields = ['highest_role']

class ListingSearchFilter(django_filters.FilterSet):
	"""
	Supports the following query params:
		* categories (AND logic)
		* agencies (OR logic)
		* listing_types (OR logic)

	Full-text search is provided via the search parameter via the
	default SearchFilter filter
	"""
	categories = django_filters.ModelMultipleChoiceFilter(conjoined=True,
		name='categories__')
    class Meta:
        model = models.Listing
        fields = ['categories']