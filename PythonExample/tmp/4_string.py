


s = 'ab,cde,fgh,ijk'
t = s.split(',')
print type(t)

class tmp(object):
    def __init__(self, a):
        print "this is init of TestWith"
        self.a=a

    def __enter__(self):
        print 'begin'
        return self

    def if_exist(self):
        self.b = self.a + 1
        return self.b

    def __exit__(self, *args):
        print "end"
        print self.b


with tmp(1) as t:
    print "haha"
    print t.if_exist()

