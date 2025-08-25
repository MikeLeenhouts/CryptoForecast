import time
def unique(s: str) -> str:
    return f"{s}_{int(time.time()*1000)}"

def asset_type_payload():
    return {"name": unique("Crypto"), "description": "Digital assets"}

def asset_payload(asset_type_id: int):
    return {"asset_name": unique("Bitcoin"), "asset_type_id": asset_type_id, "description": "BTC"}

def llm_payload():
    return {"name": unique("gpt"), "provider": "openai", "model": "gpt-4o-mini"}

def prompt_payload(llm_id: int):
    return {"title": unique("MarketPrompt"), "llm_id": llm_id, "body": "Tell me the trend"}

def survey_payload():
    return {"name": unique("DailySurvey"), "is_active": True, "description": "Baseline + follow-ups"}

def schedule_payload(survey_id: int):
    return {"survey_id": survey_id, "cron": "0 1 * * ? *", "timezone": "UTC", "enabled": True}

def crypto_query_payload(survey_id: int, asset_id: int):
    return {"survey_id": survey_id, "asset_id": asset_id, "query_text": "Predict 1h price"}

def forecast_payload(survey_id: int, query_id: int):
    return {"survey_id": survey_id, "crypto_query_id": query_id, "horizon_type": "OneHour",
            "forecast_value": {"price": 65000}, "confidence": 0.7}
