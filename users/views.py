from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.views import View
from mainpages.forms import UserEnterForm
from users.forms import UserRegisterForm
from users.models import SiteUsers,UserOneCodes
import mysql.connector
from mysql.connector import Error
import _mysql
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import random
import string
from django.core.mail import send_mail

#Необходимые константы
USERS_CONTEXTS_DIR='/etc/asterisk/users_contexts/'
CONTEXT_FILE='/etc/asterisk/extensions.conf'

# Create your views here.
def get_connect_params(config_file):
    CONNECT_PARAMS={}
    fh=open(config_file,'r',encoding='utf-8')
    for line in fh:
        if line.startswith('ip'):
            AMI_IP=line.split(':')[1].rstrip()
            CONNECT_PARAMS['ip'] = AMI_IP
        if line.startswith('user'):
            AMI_USER=line.split(':')[1].rstrip()
            CONNECT_PARAMS['user'] = AMI_USER
        if line.startswith('password'):
            AMI_PASSWORD=line.split(':')[1].rstrip()
            CONNECT_PARAMS['password'] = AMI_PASSWORD
        if line.startswith('port'):
            AMI_PORT=line.split(':')[1].rstrip()
            CONNECT_PARAMS['port'] = AMI_PORT
        if line.startswith('database'):
            DATABASE=line.split(':')[1].rstrip()
            CONNECT_PARAMS['database'] = DATABASE
    return CONNECT_PARAMS

def check_valid_user(request):
    if request.session.get('username', None):
        return True
    else:
        return Http404
def create_random_string(length):
    result=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return result

class RegistrationView(View):
    def get(self,request):
        form=UserRegisterForm
        params={}
        params['form']=form
        return render(request,'user_registration_form.html',params)

    def post(self,request):
        form=UserRegisterForm(request.POST)
        if form.is_valid():

            cd=form.cleaned_data

            #Так теперь мы создаем новго пользователя и создаем также рандомные данные для отправки
            random_string=create_random_string(40)

            user=SiteUsers.objects.create(login=cd['login'],password=cd['password'],email=cd['email'],original_name=cd['original_name'],surname=cd['surname'])
            code=UserOneCodes.objects.create(user=user,code=random_string)

            #Так теперь вот тут отправляем данные на почту, чтобы по ссылке мог зарегаться
            data="Для активации вашего аккаунта на IP Telecom пожалуста пройдите по ссылке http://192.168.1.103:8080/user/activation?code={0}".format(random_string)

            send_mail('Welcome!', data, "Yasoob",[cd['email'],], fail_silently=False)
            return HttpResponse('Все нормально')

        else:
            return render(request,'user_registration_form.html',{'form':form})

class ConfirmRegistration(View):
    def get(self,request):
        html = '''
                            Вы успешно зарегистрированны<br>
                            Перейдите в свой <a href={% url 'users:UserPage' %}>аккаунт</a>
                            '''
        try:
            code=request.GET['code']
            #Так что нам нужно по коду взять пользователя у кода поставить used или вообще удалить и у пользователя постваить активен
            code=UserOneCodes.objects.get(code=code)
            user=code.user
            #Так получили пользователя, то код можно удалять
            UserOneCodes.objects.filter(code=code).delete()
            user.activated=True
            user.save()
            request.session['username'] = user.login
            return HttpResponseRedirect('/user/')
        except IndexError:
            return Http404


class UserPage(View):
    def get(self,request):
        params={}
        if request.session.get('username',None):
            params['username']=request.session.get('username')
            return render(request,'userpage.html',params)
        else:
            return HttpResponse('Вы не можете здесь находиться')


class AddNumbers(View):
    @csrf_exempt
    @never_cache
    #@check_valid_user
    def post(self,request):
        #Это та таблица которую мы вернем в ответ на запрос пользователя
        username=request.session.get('username')
        dc={}
        for key, value in request.POST.items():
            if key.startswith('number'):
                #Если ключ начинается с number то нам нужно найти password с таким же номером в конце, то мы просто берем из ПОСТа подставляя текущий номер ключа в конец
                password=request.POST['password{0}'.format(key[-1:])]
                number=request.POST[key]
                #Теперь формируем словарь где ключом будет номер а значением пароль
                dc[number]=password

        st = '<table border="1">'
        for key, value in dc.items():
            st += '<tr><td>{0}</td><td>{1}</td></tr>'.format(key, value)
        st += '</table>'


        
        #так теперя мы тут опять сначала вставляем пользователей в БД
        CONNECT_PARAMS=get_connect_params('/var/www/asterisk_site/users/conf/mysql.conf')


        try:
        #conn = mysql.connector.connect(host=CONNECT_PARAMS['ip'], user=CONNECT_PARAMS['user'],password=CONNECT_PARAMS['password'], database=CONNECT_PARAMS['database'])
            conn=_mysql.connect(host=CONNECT_PARAMS['ip'], user=CONNECT_PARAMS['user'],passwd=CONNECT_PARAMS['password'], db=CONNECT_PARAMS['database'])

        except Exception as err:
            return HttpResponse('Could not connect to MySQL {user}, {host}, {password}, {database}, {error}'.format(host=CONNECT_PARAMS['ip'], user=CONNECT_PARAMS['user'],password=CONNECT_PARAMS['password'], database=CONNECT_PARAMS['database'],error=err))

        #cursor=conn.cursor()
        for key,value in dc.items():
            name=key+'_'+username
            query='insert into sip_peers (name,secret,type,host,allow,nat,context) values ("{0}","{1}","friend","dynamic","all","yes","{2}")'.format(name,value,username)
            conn.query(query)
        conn.close()
        #Предроложим что мы вставили теперь нам нужно создать файл в диерктории /etc/asterisk/users_contexts/username
        #а потом вставить в файл extensions.conf #include=> наш файл

        number=request.POST['number1']
        number=list(number)
        number[1:] = ['X'] * len(number[1:])
        number='_'+''.join(number)
        user_context='''[{2}]
exten=>{0},1,Answer()
exten=>{0},n,Set(USERNAME=_{2})
exten=>{0},n,Set(DESTINATION={3}{4})
exten=>{0},n,Verbose(All Work)
exten=>{0},n,Playback(tt-weasels)
exten=>{0},n,Dial(SIP/{1})
exten=>{0},n,Hangup()'''.format(number,'${DESTINATION}',username,'${EXTEN}','${USERNAME}')
        user_context_file=USERS_CONTEXTS_DIR+username
        fh=open(user_context_file,'w',encoding='UTF-8')
        fh.write(user_context)
        fh.close()

        fh=open(CONTEXT_FILE,'a',encoding='utf-8')
        user_string='\n#include "{0}"'.format(user_context_file)
        fh.write(user_string)
        fh.close()
        return HttpResponse('All ok')