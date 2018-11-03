import mysql.connector
from mysql.connector import Error
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
CONNECT_PARAMS=get_connect_params('mysql.conf')

conn = mysql.connector.connect(host=CONNECT_PARAMS['ip'], user=CONNECT_PARAMS['user'],password=CONNECT_PARAMS['password'], database=CONNECT_PARAMS['database'])
if conn.is_connected():
    print('Connected')
else:
        #except Error as err:
    print('Could not connect to MySQL {user}, {host}, {password}, {database}'.format(host=CONNECT_PARAMS['ip'], user=CONNECT_PARAMS['user'],password=CONNECT_PARAMS['password'], database=CONNECT_PARAMS['database']))
