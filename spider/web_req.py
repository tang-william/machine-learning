import urllib2
import time

urls = []
for i in range(30):
    urls.append("http://tangyuanhui.cn:8000/ocpc?sa=32&sf=32")
    # urls.append("http://ad.toutiao.com/track/activate/")

# print urls

def push_one(url):
    res = ''
    try:
        response = urllib2.urlopen(url, timeout=1)
        res = response.read()
        print res
    except Exception, e:
        print e
    return res



def main():
    t0 = time.time()
    for url in urls:
        push_one(url)

    elapsed = time.time() - t0
    msg = '\n{} flags downloaded in {:.2f}s'
    print(msg.format(len(urls), elapsed))
# 14.62s

if __name__ == '__main__':
    main()