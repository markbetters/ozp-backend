"""
ModelForms - used for validation only
"""
from django.contrib.auth.models import User
from django.forms import ModelForm, ModelMultipleChoiceField

import ozpcenter.models as models

class ProfileForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = '__all__'

class UserForm(ModelForm):
    class Meta:
        model = User
        fields =  ('username', 'email')

class BasicProfileForm(ModelForm):
    """
    A ModelForm for only the most basic user info
    """
    user = ModelMultipleChoiceField(queryset=User.objects.only('username', 'email'))
    class Meta:
        model = models.Profile
        fields = ('user',)
