"""Simple in-memory knowledge base for the EV monitoring chatbot."""

DOCUMENTS = [
    {
        "id": "battery_health_best_practices",
        "text": (
            "Battery health is best maintained by keeping charge levels between 20% and 80%. "
            "Prolonged exposure to high temperatures accelerates cell degradation. "
            "If a vehicle regularly fast charges, monitor DC fast charge sessions and flag "
            "vehicles that exceed three sessions per day for a maintenance check."
        ),
        "tags": ["battery", "maintenance", "best_practice"],
    },
    {
        "id": "charging_station_alerts",
        "text": (
            "Charging station utilization above 85% during peak hours signals the need for load balancing. "
            "Send an alert when a station is offline for more than 10 minutes to reduce driver downtime. "
            "For depots with solar support, prioritize stations attached to the solar grid between 10AM and 4PM."
        ),
        "tags": ["charging", "alerting", "operations"],
    },
    {
        "id": "range_efficiency",
        "text": (
            "Vehicles operating below 3.5 miles per kWh should be reviewed for tire pressure, "
            "driver behavior coaching, and HVAC usage audits. "
            "Cold weather drops efficiency; preconditioning the cabin while plugged in mitigates range loss."
        ),
        "tags": ["efficiency", "range", "coaching"],
    },
    {
        "id": "fleet_reporting",
        "text": (
            "Daily fleet reports should highlight vehicles with battery health below 75%, "
            "charging anomalies, and uptime percentage. "
            "Weekly summaries combine trend lines for energy consumption, cost per kWh, and alert resolution."
        ),
        "tags": ["reporting", "analytics"],
    },
    {
        "id": "demand_response",
        "text": (
            "When the utility sends a demand-response event, curtail charging on non-critical vehicles "
            "and stagger start times in 15-minute increments. "
            "Vehicles flagged as mission-critical keep minimum 80% charge buffers during events."
        ),
        "tags": ["grid", "demand_response"],
    },
]

