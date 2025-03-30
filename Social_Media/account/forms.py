from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile



class UserRegistartionForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(max_length=50, widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(max_length=20, min_length=8, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':"Password must be longer that 8 characters"}))
    confirm_password = forms.CharField(max_length=20, min_length=8, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':"Please repeat your password"}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('this email already exists')
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError('this username already exists')
        return username
    
    def clean(self):
        cd = super().clean()
        P = cd.get('password')
        CP = cd.get('confirm_password')

        if P and CP and P != CP:
            raise ValidationError('please repeat your password correctly')
        

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(max_length=20, min_length=8, widget=forms.PasswordInput(attrs={'class':'form-control'}))


class EditUserForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ('age','bio')