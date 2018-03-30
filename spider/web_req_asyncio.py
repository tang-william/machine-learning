import trollius as asyncio
from trollius import From,Return
import time

from web_req import push_one,urls


@asyncio.coroutine
def hello():
    print("Hello world!")
    r = yield From(asyncio.sleep(1))
    print("Hello again!")


@asyncio.coroutine
def wget(host):
    # print('wget %s...' % host)
    connect = asyncio.open_connection(host, 80)
    reader, writer = yield From(connect)
    header = 'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % host
    writer.write(header.encode('utf-8'))
    yield From(writer.drain())
    while True:
        line = yield From(reader.readline())
        if line == b'\r\n':
            break
        print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
    # Ignore the body, close the socket
    writer.close()

@asyncio.coroutine
def wget1(host):
    yield From(push_one(host))


def main():
    t0 = time.time()

    loop = asyncio.get_event_loop()
    tasks = [wget1(host) for host in urls]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    elapsed = time.time() - t0
    msg = '\n{} flags downloaded in {:.2f}s'
    print(msg.format(len(urls), elapsed))



if __name__ == '__main__':
    main()