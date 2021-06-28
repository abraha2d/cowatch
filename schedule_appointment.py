import asyncio

from main import schedule_appointment
from utils import close_session


async def main():
    try:
        await schedule_appointment(
            session_id="4cc43a1a-d82f-11eb-991f-57e88b855246",
            slot="12:00PM-03:00PM",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        )
    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())
