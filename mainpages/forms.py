from django import forms
class UserEnterForm(forms.Form):
    login=forms.CharField(max_length=100,widget=forms.TextInput,label='Имя входа')
    password=forms.CharField(max_length=100,widget=forms.PasswordInput,label='Пароль')