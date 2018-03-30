import json

data1 = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 }
data2 = { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 }

json1 = json.dumps(data1)
json2 = json.dumps(data2)

res = {}
res["d1"]=json1
res["d2"]=json2
res = json.dumps([res])

print res

def fun1(*arg):
    print 2
    print arg
    pass

fun1(1, 2, 3,4)