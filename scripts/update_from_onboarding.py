import json

import os

memo_file = "account_memo_v2.json"

if os.path.exists(memo_file):
    with open(memo_file, "r") as f:
        memo = json.load(f)
else:
    with open("outputs/account_memo_v1.json", "r") as f:
        memo = json.load(f)

with open("outputs/onboarding_transcript.txt", "r") as f:
    onboarding=f.read().lower()
print("Transcript loaded successfully")

changes=[]

import re

if "ben's electric" in onboarding or "bens electric" in onboarding:
    old = memo["company_name"]
    memo["company_name"] = "Ben's Electric"

    changes.append({
        "field": "company_name",
        "old": old,
        "new": "Ben's Electric",
        "reason": "Detected company name from onboarding transcript"
    })

timezone_patterns = {
    "pacific": "Pacific",
    "eastern": "Eastern",
    "central": "Central",
    "mountain": "Mountain"
}

for key, value in timezone_patterns.items():
    if key + " time" in onboarding or key + " timezone" in onboarding:
        old = memo["business_hours"]["timezone"]
        memo["business_hours"]["timezone"] = value

        changes.append({
            "field": "business_hours.timezone",
            "old": old,
            "new": value,
            "reason": "Detected timezone in onboarding transcript"
        })

        break


# -------- RESET BUSINESS HOURS IF NOT CONFIRMED --------

# -------- RESET BUSINESS HOURS FROM DEMO ASSUMPTIONS --------

old = memo["business_hours"].copy()

# Clear demo assumptions first
memo["business_hours"]["days"] = None
memo["business_hours"]["start_time"] = None
memo["business_hours"]["end_time"] = None

changes.append({
    "field": "business_hours",
    "old": old,
    "new": memo["business_hours"],
    "reason": "Reset demo-stage business hours; not confirmed during onboarding"
})

# -------- OPTIONAL: DETECT DAYS IF EXPLICITLY STATED --------

if "monday to friday" in onboarding:
    memo["business_hours"]["days"] = "Mon-Fri"

    changes.append({
        "field": "business_hours.days",
        "old": None,
        "new": "Mon-Fri",
        "reason": "Detected working days from onboarding transcript"
    })

elif "monday to saturday" in onboarding:
    memo["business_hours"]["days"] = "Mon-Sat"

    changes.append({
        "field": "business_hours.days",
        "old": None,
        "new": "Mon-Sat",
        "reason": "Detected working days from onboarding transcript"
    })


fee_match = re.search(r"(service call|call out).*?(\d{2,3})", onboarding)

if fee_match:
    fee = int(fee_match.group(2))

    if "pricing" not in memo:
        memo["pricing"] = {}

    old = memo["pricing"].get("service_call_fee")

    memo["pricing"]["service_call_fee"] = fee

    changes.append({
        "field": "pricing.service_call_fee",
        "old": old,
        "new": fee,
        "reason": "Detected service call fee from onboarding"
    })


# -------- HOURLY RATE DETECTION --------

numbers = re.findall(r"\b\d{2,3}\b", onboarding)

numbers = [int(x) for x in numbers]

possible_rates = [n for n in numbers if 40 <= n <= 110]

if possible_rates:
    rate = max(possible_rates)

    if "pricing" not in memo:
        memo["pricing"] = {}

    old = memo["pricing"].get("hourly_rate")

    memo["pricing"]["hourly_rate"] = rate

    changes.append({
        "field": "pricing.hourly_rate",
        "old": old,
        "new": rate,
        "reason": "Detected hourly rate from onboarding transcript"
    })


email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", onboarding)

if email_match:
    email = email_match.group()

    old = memo.get("notification_email")

    memo["notification_email"] = email

    changes.append({
        "field": "notification_email",
        "old": old,
        "new": email,
        "reason": "Detected email from onboarding"
    })


if "no emergency calls" in onboarding or "we don't do emergency calls" in onboarding:
    memo["after_hours"] = {
        "emergency_supported": False
    }

    changes.append({
        "field": "after_hours.emergency_supported",
        "old": None,
        "new": False,
        "reason": "Detected no emergency policy"
    })


# -------- SERVICE TYPE DETECTION --------
if "electric" in onboarding or "electrical" in onboarding:
    old = memo["services_supported"]

    memo["services_supported"] = ["electrical service calls", "electrical repairs"]

    changes.append({
        "field": "services_supported",
        "old": old,
        "new": memo["services_supported"],
        "reason": "Updated service type based on onboarding call"
    })

# -------- REMOVE DEMO EMERGENCY DEFINITIONS --------
if "electric" in onboarding:
    old = memo["emergency_definition"]

    memo["emergency_definition"] = ["power outage", "electrical fault"]

    changes.append({
        "field": "emergency_definition",
        "old": old,
        "new": memo["emergency_definition"],
        "reason": "Updated emergency definition for electrical services"
    })

if "pressure washing" in onboarding or "property manager" in onboarding:
    memo["after_hours_exception"] = "Property management client"

    changes.append({
        "field": "after_hours_exception",
        "old": None,
        "new": "Property management client",
        "reason": "Detected after-hours exception client"
    })


if memo["business_hours"].get("timezone") is not None:
    memo["questions_or_unknowns"] = [
        q for q in memo["questions_or_unknowns"]
        if "timezone" not in q.lower()
    ]

if memo.get("office_address") is not None:
    memo["questions_or_unknowns"] = [
        q for q in memo["questions_or_unknowns"]
        if "office address" not in q.lower()
    ]

with open("account_memo_v2.json", "w") as f:
    json.dump(memo, f, indent=2)

with open("changes.json", "w") as f:
    json.dump(changes, f, indent=2)