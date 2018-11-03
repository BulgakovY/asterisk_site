from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
from mainpages.forms import UserEnterForm
from users.models import SiteUsers
# Create your views here.

class MainPage(View):
    def get(self,request):
        params={}
        params['form']=UserEnterForm
        return render(request,'mainpage.html',params)

    def post(self,request):
        form=UserEnterForm(request.POST)
        if form.is_valid():
            valid_user=SiteUsers.objects.get(login=request.POST['login'],password=request.POST['password'])
            if valid_user.activated==True:
                request.session['username']=valid_user.login
                return HttpResponseRedirect('/user/')
            else:
                return HttpResponse('Уходите прочь, вы не активны. Пополните для начала счет, каким нибудь способом')
        else:
            return render(request,'mainpage.html',{'form':form})



