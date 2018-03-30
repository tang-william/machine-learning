import threading
import time

a = 3

def func1(x,queque):
    time.sleep(1)
    print 'a :' + str(a)
    queque[x] =5
    return x*x


if __name__ == '__main__':


    dict = dict()
    t1 = threading.Thread(target=func1, args=(1,dict,))
    t2 = threading.Thread(target=func1, args=(2,dict,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print dict