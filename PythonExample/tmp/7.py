


res = {'lt': 120.47866394672555, 'params': [0.47062578714505282, -0.17664012125881237], 'fit_func': 'y= 0.470625787145x**-0.176640121259', 'R2': 0.74790465035206344, 'BreakPoint': 366}

print type(res)
print res['lt']
print type(res['lt'])
a='1'
b='2'

print (a + '1' + b)


import os

os.system('ls /Users/tyh/github/')


print "hello world"
print "a * b = %d" % 10

str = "2017-12-06 08:03:27.330 [http-bio-9140-exec-396] [INFO] [?.()] - clickAd|19646930|430"

print str[0:19]
str.split("|")[1]

list = []

with open('/Users/tyh/Downloads/clickAd.txt', 'r') as f:
    for str in f.readlines():
        time = str[0:19]
        uid = str.split("|")[1]
        line  = time
        line += ","
        line += uid
        list.append(line)

print list
with open('/Users/tyh/Downloads/clickAd.csv', 'w') as f:
    lists = [line + "\n" for line in list]
    f.writelines(lists)
