# Rename this file to config.py and fill it out

MOBILE = "9111796187"
BENEFICIARIES = [
    "88661584796342",
    "73919930937417",
]

DOSE = "1"  # "1" or "2"
MIN_AGE_LIMIT = "45"  # "18", "40", and "45" are common

# Districts to search in for available appointments
# "https://cdn-api.co-vin.in/api/v2/admin/location/states" to get a list of state IDs
# "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}" to get a list of district IDs
DISTRICTS = [
    "270",  # Bagalkot
    "276",  # Bangalore Rural
    "265",  # Bangalore Urban
]

# How many days to look into the future (max 7)
# 1 means only look for appointments available today
LOOKAHEAD = 2

# API docs say max 100 calls in 5 minutes
# Increase at your own risk
MAX_CALLS_PER_MIN = 20

# Squid proxy to get around IP address restrictions in the API
PROXY = "http://squid.example.com:3128"
