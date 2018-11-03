from django.db import models

# Create your models here.
class SiteUsers(models.Model):
    login=models.CharField(max_length=100,verbose_name='Логин',blank=False,unique=True)
    password=models.CharField(max_length=100,verbose_name='Пароль',blank=False)
    email=models.EmailField(max_length=150,verbose_name='Email',blank=False,unique=True)
    original_name=models.CharField(max_length=100,verbose_name='Имя пользователя',blank=True)
    surname=models.CharField(max_length=100,verbose_name='Фамилия пользователя',blank=True)
    bill=models.FloatField(verbose_name='Счет',default=0.00)
    activated=models.BooleanField(verbose_name='Активен',default=False)
    creation_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.login)

class UserOneCodes(models.Model):
    user=models.OneToOneField(SiteUsers,on_delete=models.CASCADE)
    code=models.CharField(max_length=100,verbose_name='Одноразовый код')
    used=models.BooleanField(verbose_name='Использован',default=False)

    def __str__(self):
        return str(self.user)