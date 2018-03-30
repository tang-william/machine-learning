
import re

log = "123.126.111.162 - - [07/Dec/2017:20:06:06 +0800] 335 \"GET /push_test?v=v1&article_id=3319644&appVersion=2.6.2.5&imei=866333024898262&action=receive&userId=24592700&push_id=500011&timestamp=1512648365965&os_version=6.0.1&model=MI 4LTE HTTP/1.1\" 200 310 0 \"-\" \"Dalvik/2.1.0 (Linux; U; Android 6.0.1; MI 4LTE MIUI/7.11.30)\" \"-\" \"0.000\" \"-\" \"-\" \"-\" "
matchObj = re.match(r'(.*) - - \[(.*)\] (.*) \/(.*)\?(.*)\sHTTP(.*)', log, re.I)

print matchObj.group(1)
print matchObj.group(2)
print matchObj.group(4)
param = matchObj.group(5)

dict = {}
list = param.split("&")
for i in list:
    a = i.split("=")
    dict[a[0]] = a[1]

print dict

