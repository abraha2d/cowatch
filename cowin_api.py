API_BASE = "https://cdn-api.co-vin.in/api/v2"

AUTH_BASE = API_BASE + "/auth"
GENERATE_MOBILE_OTP = AUTH_BASE + "/generateMobileOTP"
VALIDATE_MOBILE_OTP = AUTH_BASE + "/validateMobileOtp"

APPOINTMENT_BASE = API_BASE + "/appointment"
CENTERS_BASE = APPOINTMENT_BASE + "/centers/public"
SESSIONS_BASE = APPOINTMENT_BASE + "/sessions/public"

FIND_BY_PIN = SESSIONS_BASE + "/findByPin"
FIND_BY_DISTRICT = SESSIONS_BASE + "/findByDistrict"
FIND_BY_LAT_LONG = CENTERS_BASE + "/findByLatLong"

CALENDAR_BY_PIN = SESSIONS_BASE + "/calendarByPin"
CALENDAR_BY_DISTRICT = SESSIONS_BASE + "/calendarByDistrict"
CALENDAR_BY_CENTER = SESSIONS_BASE + "/calendarByCenter"

SCHEDULE_APPOINTMENT = APPOINTMENT_BASE + "/schedule"
CANCEL_APPOINTMENT = APPOINTMENT_BASE + "/cancel"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
}
SECRET = "U2FsdGVkX1/OUHg66F6tQdoWnhADI1mzMlI1hO7O6VihQv0t7C7vo7BM4ZU7dKpuYtEA4k1iFyqpyVlNHN16YQ=="
