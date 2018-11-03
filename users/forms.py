from django import forms
from django.forms import ModelForm
from users.models import SiteUsers
class UserEnterForm(forms.Form):
    login=forms.CharField(max_length=100,widget=forms.TextInput,label='Имя входа')
    password=forms.CharField(max_length=100,widget=forms.PasswordInput,label='Пароль')

class UserRegisterForm(ModelForm):
    class Meta:
        model=SiteUsers
        fields=['login','password','email','original_name','surname']
