from multiprocessing import Pool,Process
import time
import os

def info():
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def run(x):
    info()
    time.sleep(1)
    print x**x
    return x*x

def func1(x):
    info()
    time.sleep(1)
    print 'func1'
    return x*x


def func2(x):
    info()
    time.sleep(1)
    print 'func2'
    return x*x

def pool1():
    testFL = [1, 2, 3, 4, 5, 6]

    s = time.time()
    for fn in testFL:
        run(fn)
    e1 = time.time()
    print  int(e1 - s)

    p = Pool(5)
    result = p.map(run, testFL)
    print result
    e2 = time.time()
    print  int(e2 - e1)


def join1():
    p1 = Process(target=run, args=(1,))
    p1.start()

    p2 = Process(target=run, args=(2,))
    p2.start()

    p1.join()
    p2.join()

    print 'master begin'
    info()


if __name__ == '__main__':

    pool = Pool(3)

    s = time.time()
    result1 = pool.apply_async(func1, (1,))
    result2 = pool.apply_async(func2, (2,))
    result3 = pool.apply_async(func2, (3,))

    print type(result1.get())
    print result2.get()
    print result3.get()

    e = time.time()
    print  int(e - s)

    pool.close()
    pool.join()
