import time

from concurrent import futures

from web_req import push_one,urls


WORKERS = 20



def download_many(urls):
    workers = min(WORKERS, len(urls))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(push_one, urls)

    print list(res)
    return len(list(res))

def main():
    t0 = time.time()

    count = download_many(urls)

    elapsed = time.time() - t0
    msg = '\n{} flags downloaded in {:.2f}s'
    print(msg.format(count, elapsed))


if __name__ == '__main__':
    main()