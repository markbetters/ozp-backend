"""
ModelForms - used for validation only
"""
from django.forms import ModelForm

import ozpcenter.models as models

class ProfileForm(ModelForm):
	class Meta:
		model = models.Profile
		fields = '__all__'
