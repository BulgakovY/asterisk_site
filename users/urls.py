from django.contrib import admin
from django.urls import path,re_path
from mainpages.views import MainPage
from users.views import UserPage,AddNumbers,RegistrationView,ConfirmRegistration
app_name='users'
urlpatterns = [
    path('',UserPage.as_view(),name='UserPage'),

    path('add_numbers/',AddNumbers.as_view()),
    path('register/',RegistrationView.as_view(),name='RegisterNewUser'),
    path('activation',ConfirmRegistration.as_view())
]