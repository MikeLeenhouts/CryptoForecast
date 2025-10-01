# Proposed Data provided by One-Time Event Bridge trigger
# asset_name, asset_symbol, llm_name, llm_model,prompt


import json
from typing import Dict, Any

# Import the LLM-specific query functions
from get_asset_recommendation_Anthropic import get_asset_recommendation_Anthropic
from get_asset_recommendation_Gemini import get_asset_recommendation_Gemini
from get_asset_recommendation_Grok import get_asset_recommendation_Grok
from get_asset_recommendation_OpenAI import get_asset_recommendation_OpenAI


def forecast_worker(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Worker function that queries the correct LLM based on survey configuration.
    This will be invoked by EventBridge Scheduler (via Lambda in LocalStack).

    Args:
        event: The input payload from EventBridge Scheduler.
            Example:
            {
                "survey_id": 123,
                "asset_name": "Bitcoin",
                "llm_name": "Anthropic",
                "llm_model": "claude-opus-4-1-20250805",
                "prompt": "Provide a recommendation for the asset {asset_name}..."
            }
        context: (optional) AWS Lambda context (ignored in LocalStack tests)

    Returns:
        Dict containing recommendation, confidence, explanation, and references
    """

    survey_id = event.get("survey_id")
    asset_name = event.get("asset_name", "Unknown")
    llm_name = event.get("llm_name")
    llm_model = event.get("llm_model")
    prompt = event.get("prompt")

    if not llm_name:
        raise ValueError("Missing 'llm_name' in event payload")

    # Dispatch table for LLM calls
    llm_dispatch = {
        "Anthropic": get_asset_recommendation_Anthropic,
        "Gemini": get_asset_recommendation_Gemini,
        "Grok": get_asset_recommendation_Grok,
        "OpenAI": get_asset_recommendation_OpenAI,
    }

    if llm_name not in llm_dispatch:
        raise ValueError(f"Unsupported llm_name '{llm_name}'. Must be one of {list(llm_dispatch.keys())}")

    # Call the right LLM query function
    result = llm_dispatch[llm_name](asset_name, prompt, llm_model)

    # Convert result to dict for downstream storage/logging
    response = {
        "survey_id": survey_id,
        "llm_name": llm_name,
        "asset_name": asset_name,
        "recommendation": result.recommendation.value,
        "confidence": result.confidence,
        "explanation": result.explanation,
        "references": result.references,
    }

    print(f"[forecast_worker] Response: {json.dumps(response, indent=2)}")
    return response
