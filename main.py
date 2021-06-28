#!/usr/bin/env python3

import asyncio
import traceback
from datetime import datetime, timedelta
from hashlib import sha256
from time import sleep

import pytz
from dateutil.rrule import rrule, DAILY

from config import *
from cowin_api import *
from utils import close_session, fetch, flatten, gather


def session_predicate(s):
    if s["vaccine"] != "COVISHIELD":
        return False

    if int(s["min_age_limit"]) != MIN_AGE_LIMIT:
        return False

    if int(s[f"available_capacity_dose{DOSE}"]) < len(BENEFICIARIES):
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
    max_date = now_date + timedelta(days=LOOKAHEAD - 1)
    search_strs = [d.strftime("%d-%m-%Y") for d in rrule(DAILY, dtstart=now_date, until=max_date, count=LOOKAHEAD)]
    print(search_strs)

    data = await gather(
        fetch(
            FIND_BY_DISTRICT,
            district_id=district_id,
            date=search_str,
            top_level="sessions"
        ) for district_id in DISTRICTS for search_str in search_strs
    )

    sessions = flatten(data)
    sessions = filter(session_predicate, sessions)
    sessions = list(sessions)
    # pprint(sessions)

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
        for slot in session['slots']:
            print(f"  - {slot}")
        print(f"- Address: {session['address']}")
        print(f"- Fee: {session['fee']} INR")

    return sessions


async def generate_otp():
    txn_id = await fetch(GENERATE_MOBILE_OTP, mobile=MOBILE, secret=SECRET, top_level="txnId", method="POST")
    print(txn_id)
    return txn_id


async def validate_otp(txn_id, otp):
    m = sha256()
    m.update(otp.encode())
    otp_hash = m.digest().hex()

    token = await fetch(VALIDATE_MOBILE_OTP, txnId=txn_id, otp=otp_hash, top_level="token", method="POST")
    print(token)
    return token


async def schedule_appointment(session_id, slot, token):
    acn = await fetch(
        SCHEDULE_APPOINTMENT,
        dose=DOSE,
        session_id=session_id,
        slot=slot,
        beneficiaries=BENEFICIARIES,
        top_level="appointment_confirmation_no",
        method="POST",
        token=token,
    )
    print(acn)
    return acn


def get_token():
    txn_id = generate_otp()
    otp = ""
    while otp == "":
        otp = input("Please enter the OTP: ")
        try:
            return validate_otp(txn_id, otp)
        except Exception:
            txn_id = generate_otp()
            otp = ""


async def main():
    token = None
    cycle_delay = (60 * len(DISTRICTS) * LOOKAHEAD) / MAX_CALLS_PER_MIN

    while True:
        try:
            if token is None:
                token = ""
            else:
                print(f"Sleeping for {cycle_delay} seconds...")
                sleep(cycle_delay)

            sessions = await find_sessions()
            if len(sessions) == 0:
                continue

            if not token:
                # input("Press ENTER to send an OTP: ")
                token = get_token()

            for session in sessions:
                try:
                    acn = schedule_appointment(session['session_id'], session['slots'][-1], token)
                except Exception:
                    traceback.print_exc()
                    token = get_token()
                    acn = schedule_appointment(session['session_id'], session['slots'][-1], token)
                if acn is not None:
                    print(
                        "Booked appointment"
                        f" at {session['name']}"
                        f" on {session['date']}"
                        f" between {session['slots'][-1]}"
                    )
                    print(f"District: {session['district_name']}    Address: {session['address']}")
                    print(f"Fee: {session['fee']} INR    Confirmation ID: {acn}")
                    return
        finally:
            pass

    await close_session()


if __name__ == "__main__":
    asyncio.run(main())
