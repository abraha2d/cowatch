import asyncio

from main import generate_otp
from utils import close_session


async def main():
    try:
        await generate_otp()
    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())
