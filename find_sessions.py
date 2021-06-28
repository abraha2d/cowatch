import asyncio

from main import find_sessions
from utils import close_session


async def main():
    try:
        await find_sessions()
    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())
