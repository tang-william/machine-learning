# -*- coding: utf-8 -*-
# file: example1.py
import string

# 这个是 str 的字符串
s = '关关雎鸠'
# 这个是 unicode 的字符串
u = u'关关雎鸠'
print isinstance(s, str)      # True
print isinstance(u, unicode)  # True
print s.__class__  # <type 'str'>
print u.__class__  # <type 'unicode'>


print u.encode('utf-8') + s
print s
print u.encode('utf-8')




import traceback

try:
    a = 1 / 0
except Exception:
    print 1
    print type(traceback.format_exc())

import redis
r = redis.StrictRedis(host='redis-xinwenzhuan.coohua-inc.com', port=6379)