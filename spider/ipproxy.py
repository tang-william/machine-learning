import requests
import json

r = requests.get('http://47.88.78.74:8000/?types=0&count=5')
ip_ports = json.loads(r.text)
print ip_ports

ip = ip_ports[0]['ip']

port = ip_ports[0]['port']

proxies={

    'http':'http://%s:%s'%(ip,port),

    'https':'http://%s:%s'%(ip,port)

}

r = requests.get('http://ip.chinaz.com/',proxies=proxies)

r.encoding='utf-8'

print r.text