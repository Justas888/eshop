from django import forms
from .models import Profile, User, Client


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('picture',)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['address', 'phone_number']
