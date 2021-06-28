import asyncio

from main import validate_otp
from utils import close_session


async def main():
    try:
        await validate_otp(txn_id="ac4d5ffc-d82f-11eb-af62-67b37bb75985", otp="686354")
    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())
