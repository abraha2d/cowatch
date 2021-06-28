import asyncio
import random
from datetime import datetime
from json import JSONDecodeError
from traceback import print_exc

from aiohttp import ClientError, ClientSession

from config import PROXIES
from cowin_api import HEADERS

client_session: ClientSession = None


def get_session():
    global client_session
    if client_session is None:
        client_session = ClientSession()
    return client_session


async def close_session():
    global client_session
    if client_session is not None:
        await client_session.close()


async def fetch(endpoint, top_level, method="GET", token=None, on_error=None, **kwargs):
    print(f"DEBUG:{datetime.now()}:{method}:{endpoint}")
    print(f"DEBUG:{datetime.now()}:DATA:{kwargs}")

    session = get_session()

    if method == "GET":
        method = session.get
        data = {"params": kwargs}
    elif method == "POST":
        method = session.post
        data = {"json": kwargs}
    else:
        raise Exception(f"Unknown method {method}")

    headers = HEADERS
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    proxy = random.choice(PROXIES)
    print(f"DEBUG:{datetime.now()}:PROXY:{proxy}")

    async with method(
        endpoint,
        **data,
        headers=HEADERS,
        proxy=proxy,
    ) as response:
        try:
            if data.get("params", None) is None:
                print(
                    f"DEBUG:{datetime.now()}:"
                    f"RESP:{await response.json(content_type=None)}"
                )
            return (await response.json(content_type=None)).get(top_level)
        except JSONDecodeError:
            raise Exception(await response.text())
        except ClientError:
            if on_error is None:
                raise
            else:
                print_exc()
                return on_error


async def gather(coroutines):
    return await asyncio.gather(*coroutines)


def flatten(ll):
    return (i for sl in ll for i in sl)
