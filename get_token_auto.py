import asyncio

from main import get_token_auto
from utils import close_session


async def main():
    try:
        await get_token_auto()
    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())
