"""
Views
"""
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.serializers as serializers
import ozpcenter.models as models

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

class ContactTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ContactType.objects.all()
    serializer_class = serializers.ContactTypeSerializer

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = models.Agency.objects.all()
    serializer_class = serializers.AgencySerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def metadataView(request):
	"""
	Metadata for the store including categories, agencies, contact types,
	intents, and listing types
	"""
	queryset_categories = models.Category.objects.all().values('title',
		'description')
	queryset_listing_types = models.ListingType.objects.all().values('title',
		'description')
	queryset_agencies = models.Agency.objects.all().values('title',
		'short_name', 'icon_url')
	queryset_contact_types = models.ContactType.objects.all().values('name',
		'required')
	queryset_intents = models.Intent.objects.all().values('action',
		'media_type', 'label', 'icon')

	res = {
	'categories': queryset_categories,
	'listing_types': queryset_listing_types,
	'organizations': queryset_agencies,
	'contact_types': queryset_contact_types,
	'intents': queryset_intents}
	return Response(res)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def current_user(request):
	user = request.user
	return Response({
	    'username': user.username,
	    'email': user.email
	})
