import trollius as asyncio
from trollius import From,Return
import itertools
import sys


@asyncio.coroutine  # <1>
def spin(msg):  # <2>
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))
        try:
            yield From(asyncio.sleep(.1))  # <3>
        except asyncio.CancelledError:  # <4>
            break
    write(' ' * len(status) + '\x08' * len(status))


@asyncio.coroutine
def slow_function():  # <5>
    # pretend waiting a long time for I/O
    yield From(asyncio.sleep(3))  # <6>
    raise Return("suc")


@asyncio.coroutine
def supervisor():  # <7>
    spinner = asyncio.async(spin('thinking!'))  # <8>
    print('spinner object:', spinner)  # <9>
    result = yield From(slow_function())  # <10>
    spinner.cancel()  # <11>
    raise Return(result)


def main():
    loop = asyncio.get_event_loop()  # <12>
    result = loop.run_until_complete(supervisor())  # <13>
    loop.close()
    print('Answer:', result)


if __name__ == '__main__':
    main()