"""
Views for testing authentication and authorization info
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

import ozpcenter.models as models
import ozpcenter.permissions as perms


@api_view(['GET'])
@permission_classes((perms.IsOrgSteward, ))
def test(request):
	profile = models.Profile.objects.get(username=request.user.username)
	group_perms = request.user.get_group_permissions()
	all_perms = request.user.get_all_permissions()
	return Response({
		'request.user.username': request.user.username,
		'profile.username': profile.username,
		'profile.bio': profile.bio,
		'group_perms': group_perms,
		'all_perms': all_perms})