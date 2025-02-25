from django import forms
from .models import Profile, User, Client


class ProfileUpdateForm(forms.ModelForm):
    """
    Formos klasė, skirta vartotojo profilio nuotraukos atnaujinimui.
    Leidžia vartotojui atnaujinti savo profilio nuotrauką.
    """
    class Meta:
        model = Profile
        fields = ('picture',)


class UserUpdateForm(forms.ModelForm):
    """
    Formos klasė, skirta vartotojo el. pašto atnaujinimui.
    Leidžia vartotojui atnaujinti savo el. pašto adresą.
    """
    class Meta:
        model = User
        fields = ('email',)


class ClientUpdateForm(forms.ModelForm):
    """
    Formos klasė, skirta kliento informacijos atnaujinimui.
    Leidžia vartotojui atnaujinti savo vardą, pavardę, adresą ir telefono numerį.
    """
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'address', 'phone_number']
