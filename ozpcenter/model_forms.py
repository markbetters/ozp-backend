"""
ModelForms - used for validation only
"""
from django.forms import ModelForm

import ozpcenter.models as models

class ProfileForm(ModelForm):
	class Meta:
		model = models.Profile
		fields = '__all__'

class BasicProfileForm(ModelForm):
	"""
	A ModelForm for only the most basic user info
	"""
	class Meta:
		model = models.Profile
		fields = ['username', 'email']
