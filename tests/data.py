# tests/data.py
import time
from datetime import datetime, timezone, timedelta

def unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time()*1000)}"

# ---- Asset Types / Assets
def asset_type_payload():
    return {
        "asset_type_name": unique("Crypto"),
        "description": "Digital assets",
    }

def asset_payload(asset_type_id: int):
    return {
        "asset_type_id": asset_type_id,
        "asset_name": unique("Bitcoin"),
        "description": "BTC",
    }

# ---- LLMs / Prompts
def llm_payload():
    return {
        "llm_name": unique("gpt"),
        "api_url": "https://api.fake/v1/chat/completions",
        "api_key_secret": "TEST_ONLY_DO_NOT_USE",
    }

def prompt_payload(llm_id: int):
    return {
        "llm_id": llm_id,
        "prompt_text": "Given the asset context, provide a baseline market analysis.",
        "prompt_version": 1,
    }

# ---- Schedules / Query Schedules
def schedule_payload():
    return {
        "schedule_name": unique("Daily-1AM"),
        "schedule_version": 1,
        "initial_query_time": "01:00:00",
        "timezone": "America/Chicago",
        "description": "Baseline at 1AM local",
    }

def query_schedule_baseline(schedule_id: int):
    # Initial Baseline @ T0
    return {
        "schedule_id": schedule_id,
        "query_type_id": 1,  # Initial Baseline
        "delay_hours": 0,
        "paired_followup_delay_hours": None,
    }

def query_schedule_bf(schedule_id: int, target_delay: int):
    # Baseline Forecast @ T0 paired to a follow-up target
    return {
        "schedule_id": schedule_id,
        "query_type_id": 2,  # Baseline Forecast
        "delay_hours": 0,
        "paired_followup_delay_hours": target_delay,
    }

def query_schedule_followup(schedule_id: int, delay: int):
    # Follow-up at +delay
    return {
        "schedule_id": schedule_id,
        "query_type_id": 3,  # Follow-up
        "delay_hours": delay,
        "paired_followup_delay_hours": None,
    }

# ---- Surveys
def survey_payload(asset_id: int, schedule_id: int, prompt_id: int, is_active: bool = True):
    return {
        "asset_id": asset_id,
        "schedule_id": schedule_id,
        "prompt_id": prompt_id,
        "is_active": is_active,
    }

# ---- Crypto Queries / Forecasts
def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()

def cq_initial(survey_id: int, schedule_id: int, t0_utc: datetime):
    return {
        "survey_id": survey_id,
        "schedule_id": schedule_id,
        "query_type_id": 1,          # Initial Baseline
        "target_delay_hours": None,  # only for BF @ T0
        "scheduled_for_utc": utc_iso(t0_utc),
        "status": "PLANNED",
    }

def cq_baseline_forecast(survey_id: int, schedule_id: int, t0_utc: datetime, target_delay: int):
    return {
        "survey_id": survey_id,
        "schedule_id": schedule_id,
        "query_type_id": 2,           # Baseline Forecast
        "target_delay_hours": target_delay,
        "scheduled_for_utc": utc_iso(t0_utc),
        "status": "PLANNED",
    }

def cq_followup(survey_id: int, schedule_id: int, t0_utc: datetime, delay: int):
    return {
        "survey_id": survey_id,
        "schedule_id": schedule_id,
        "query_type_id": 3,           # Follow-up
        "target_delay_hours": None,
        "scheduled_for_utc": utc_iso(t0_utc + timedelta(hours=delay)),
        "status": "PLANNED",
    }

def forecast_payload(query_id: int, horizon_label: str = "OneHour"):
    return {
        "query_id": query_id,
        "horizon_type": horizon_label,
        "forecast_value": {"price": 65000, "note": "seed"},
    }
