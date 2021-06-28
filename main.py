#!/usr/bin/env python3

import asyncio
import re
import sqlite3
from datetime import datetime
from hashlib import sha256
from os.path import expanduser
from time import sleep, time

import pytz
from dateutil.rrule import rrule, DAILY

from config import *
from cowin_api import *
from utils import close_session, fetch, flatten, gather


def session_predicate(s):
    if s["vaccine"] != "COVISHIELD":
        return False

    if int(s["min_age_limit"]) < MIN_AGE_LIMIT:
        return False

    if int(s[f"available_capacity_dose{DOSE}"]) == 0:
        return False

    return True


async def find_sessions():
    timezone_ist = pytz.timezone("Asia/Kolkata")
    now_date = datetime.now(timezone_ist).date()
    # now_str = now_date.strftime("%d-%m-%Y")
    #
    # data = await gather(
    #     fetch(CALENDAR_BY_DISTRICT, district_id=district_id, date=now_str, top_level="centers")
    #     for district_id in DISTRICTS
    # )
    #
    # sessions = flatten(center['sessions'] for center in flatten(data))
    # max_date = max(datetime.strptime(session['date'], "%d-%m-%Y").date() for session in sessions)
    search_strs = [
        d.strftime("%d-%m-%Y") for d in rrule(DAILY, dtstart=now_date, count=LOOKAHEAD)
    ]

    data = await gather(
        fetch(
            FIND_BY_DISTRICT,
            district_id=district_id,
            date=search_str,
            top_level="sessions",
        )
        for district_id in DISTRICTS
        for search_str in search_strs
    )

    sessions = flatten(data)
    sessions = filter(session_predicate, sessions)
    sessions = list(sessions)

    for session in sessions:
        print()
        print(f"{session['session_id']}:")
        print(
            f"- Availability: {session['vaccine']}"
            f" D1={session['available_capacity_dose1']},"
            f" D2={session['available_capacity_dose2']}"
            f" (age {session['min_age_limit']}+)"
        )
        print(f"- On {session['date']} @ {session['name']}")
        for slot in session["slots"]:
            print(f"  - {slot}")
        print(f"- Address: {session['address']}")
        print(f"- District: {session['district_name']}")
        print(f"- Fee: {session['fee']} INR")

    if len(sessions) > 0:
        print()

    return sessions


async def generate_otp():
    txn_id = await fetch(
        GENERATE_MOBILE_OTP,
        mobile=MOBILE,
        secret=SECRET,
        top_level="txnId",
        method="POST",
    )
    print(f"txn_id: {txn_id}")
    return txn_id


async def validate_otp(txn_id, otp):
    m = sha256()
    m.update(otp.encode())
    otp_hash = m.digest().hex()

    token = await fetch(
        VALIDATE_MOBILE_OTP,
        txnId=txn_id,
        otp=otp_hash,
        top_level="token",
        method="POST",
    )
    print(f"token: {token}")
    return token


async def schedule_appointment(
    session_id, slot, token, num_beneficiaries=len(BENEFICIARIES)
):
    acn = await fetch(
        SCHEDULE_APPOINTMENT,
        dose=DOSE,
        session_id=session_id,
        slot=slot,
        beneficiaries=BENEFICIARIES[0:num_beneficiaries],
        top_level="appointment_confirmation_no",
        method="POST",
        token=token,
    )
    print(f"acn: {acn}")
    return acn


async def get_token():
    while True:
        txn_id = await generate_otp()
        otp = input("OTP requested. Please enter it: ")
        try:
            return await validate_otp(txn_id, otp)
        except Exception:
            print("Validation failed!")


async def get_token_auto():
    con = sqlite3.connect(expanduser("~/Library/Messages/chat.db"))
    cur = con.cursor()
    query = """select text, date from message inner join handle on handle.rowid = handle_id
     where uncanonicalized_id = "AX-NHPSMS" order by date desc limit 1"""

    while True:
        _, last_date = cur.execute(query).fetchone()
        txn_id, otp = await generate_otp(), ""

        s = time()
        while otp == "" and time() - s < 300:
            t, d = cur.execute(query).fetchone()
            if d != last_date:
                otp = re.search("\d{6}", t).group(0)
            else:
                sleep(1)

        if otp != "":
            try:
                return await validate_otp(txn_id, otp)
            except Exception:
                print("Validation failed!")


async def main():
    token, token_ts = None, None
    cycle_delay = (60 * len(DISTRICTS) * LOOKAHEAD) / MAX_CALLS_PER_MIN

    while True:
        s = time()
        try:
            sessions = await find_sessions()
            if len(sessions) == 0:
                continue

            for session in sessions:
                if token is None or token_ts - time() > 1000:
                    token, token_ts = await get_token_auto(), time()
                num_beneficiaries = max(
                    len(BENEFICIARIES), session[f"available_capacity_dose{DOSE}"]
                )
                acn = await schedule_appointment(
                    session["session_id"],
                    session["slots"][-1],
                    token,
                    num_beneficiaries,
                )
                if acn is not None:
                    print()
                    print(
                        "Booked appointment"
                        f" at {session['name']}"
                        f" on {session['date']}"
                        f" between {session['slots'][-1]}"
                        f" for {num_beneficiaries} persons."
                    )
                    print(
                        f"District: {session['district_name']}    Address: {session['address']}"
                    )
                    print(f"Fee: {session['fee']} INR    Confirmation ID: {acn}")
                    print()
                    await close_session()
                    return
        finally:
            e = time() - s
            d = max(cycle_delay - e, 0)
            print(f"Sleeping for {d:.3f} seconds... ", end="", flush=True)
            sleep(d)
            print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
