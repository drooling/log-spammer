import argparse

import httpx
import trio

from colorama import Fore, init
init(autoreset=True)

SENT_COUNT = 0


async def send_req(link: str, session: httpx.AsyncClient):
    global SENT_COUNT

    for _ in range(10):
        await session.get(str(link), headers=HEADERS)
        SENT_COUNT += 1
        print(f"[ {Fore.GREEN}REQUESTS SENT{Fore.RESET} ] -> {SENT_COUNT}",
              end='\r', flush=True)


async def core():
    global HEADERS

    parser = argparse.ArgumentParser()
    parser.add_argument("link", action="store", help="IP logger url to spam")
    parser.add_argument("-ua", action="store", metavar="User Agent", dest="ua",
                        help="User-Agent header to send on request", default="github.com/drooling")
    parser.add_argument("-ref", action="store", metavar="Referer", dest="ref",
                        help="Referrer header to send on request", default="github.com/drooling")
    parser.add_argument("--amount", type=int, action="store",
                        help="How many requests to send", default=100)
    parser.add_argument("--proxy", action="store", metavar="Proxy",
                        dest="proxy", help="Proxy to route requests through")
    parser.add_argument("--proxy-protocol", action="store", metavar="Protocol",
                        dest="proxy_proto", help="Protocol of specified proxy", default="http")
    args = parser.parse_args()

    if (args.proxy is not None):
        PROXY = {
            "all://": f"{args.proxy_proto}://{args.proxy}"
        }
    else:
        PROXY = None

    HEADERS = {"User-Agent": str(args.ua), "Referer": str(args.ref)}

    async with httpx.AsyncClient(proxies=PROXY) as session:
        async with trio.open_nursery() as nursery:
            for _ in range(int(args.amount // 10)):
                nursery.start_soon(send_req, args.link, session)

if __name__ == "__main__":
    trio.run(core)
