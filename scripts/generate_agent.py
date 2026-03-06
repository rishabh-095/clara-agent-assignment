import json

# ---- LOAD MEMO ----
with open("account_memo_v2.json", "r") as f:
    memo = json.load(f)

print(memo["company_name"])


# ---- CLEAN BUSINESS HOURS ----
days = memo["business_hours"]["days"] or "Not specified"

start = memo["business_hours"]["start_time"]
end = memo["business_hours"]["end_time"]

if start and end:
    hours_text = f"{start} to {end}"
else:
    hours_text = "Not specified"

timezone = memo["business_hours"]["timezone"] or "Not specified"


# ---- CLEAN ADDRESS ----
address = memo["office_address"] or "Not provided"


# ---- BUILD SYSTEM PROMPT ----
system_prompt = f"""
You are the voice assistant for {memo["company_name"]}.

Office Address:
{address}

Business Hours:
{days}
{hours_text}

Timezone:
{timezone}

Services Supported:
{", ".join(memo["services_supported"])}

Emergency situations include:
{", ".join(memo["emergency_definition"])}

If a caller reports an emergency:
1. Immediately collect their name
2. Collect their phone number
3. Collect the service address
4. Transfer the call to the on-call technician

If transfer fails:
- Apologize
- Inform the caller someone will call back shortly

During business hours:

Do not mention internal tools or system actions to the caller.
1. Greet the caller professionally
2. Ask the reason for their call
3. Collect the caller's name and phone number
4. Determine whether the request is emergency or non-emergency
5. Route or transfer the call appropriately
6. If transfer fails, inform the caller someone will follow up
7. Ask if they need anything else
8. Close the call politely

After business hours:

1. Greet the caller
2. Ask the reason for their call
3. Determine whether it is an emergency

If emergency:
- Collect name
- Collect phone number
- Collect service address
- Transfer immediately to the on-call technician

If transfer fails:
- Apologize
- Inform the caller someone will contact them shortly

If non-emergency:
- Collect request details
- Inform the caller the team will follow up during business hours
"""


# ---- BUILD AGENT SPEC ----
agent_spec = {
    "agent_name": memo["company_name"] + " Assistant",
    "voice_style": "professional and calm",
    "system_prompt": system_prompt,
    "version": "v2",
    "key_variables": {
        "business_hours": memo["business_hours"],
        "services_supported": memo["services_supported"],
        "emergency_definition": memo["emergency_definition"]
    },
    "call_transfer_protocol": {
        "target": memo["emergency_routing_rules"]["route_to"],
        "timeout_seconds": memo["call_transfer_rules"]["timeout_seconds"]
    }
}


# ---- SAVE AGENT SPEC ----
with open("agent_spec_v2.json", "w") as f:
    json.dump(agent_spec, f, indent=2)

print("Agent spec v2 generated.")