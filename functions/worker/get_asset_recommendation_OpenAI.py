from openai import OpenAI
from enum import Enum
from pydantic import BaseModel, Field
from os import getenv

llm_name= "OpenAI"
llm_model = "gpt-4o"

asset_name="Bitcoin"
prompt = "Provide a recommendation for the asset {asset_name}. Include a buy, sell, or hold recommendation, a confidence level between 0.0 and 1.0, a brief explanation, and any relevant references."

LLM_API_KEY_ID = llm_name + "_API_KEY"
LLM_API_KEY = str(getenv(LLM_API_KEY_ID))

LLM_BASE_URL_ID = llm_name + "_BASE_URL_ID"
LLM_BASE_URL = str(getenv(LLM_BASE_URL_ID))

# Initialize OpenAI client
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

class Recommendation(Enum):
    BUY = "Buy"
    SELL = "Sell"
    HOLD = "Hold"

class AssetRecommendation(BaseModel):
    recommendation: Recommendation = Field(..., description="Recommendation= Buy, Sell, or Hold")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level between 0.0 and 1.0")
    explanation: str = Field(..., description="Brief explanation of why")
    references: str = Field(..., description="References, e.g., 'Wall Street Journal, NY Stock Exchange'")

def get_asset_recommendation_OpenAI(asset_name: str, prompt: str,model: str) -> AssetRecommendation:
    prompt_asset = prompt.format(asset_name=asset_name)
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful investment advisor. Provide a structured recommendation for the specified asset, including a buy/sell/hold recommendation, confidence level, explanation, and references."
                },
                {
                    "role": "user",
                    "content": prompt_asset
                }
            ],
            response_format=AssetRecommendation
        )
        recommendation = response.choices[0].message.parsed
        if not recommendation:
            raise Exception("Failed to parse response from OpenAI")
        return recommendation
    except Exception as e:
        raise Exception(f"Error getting recommendation from OpenAI: {str(e)}")

Result = get_asset_recommendation_OpenAI(asset_name, prompt, llm_model)

# Assign the four LLM Query Return values to variables for database storage
recommendation = Result.recommendation.value  # Extract the string value from the enum
confidence = Result.confidence
explanation = Result.explanation
references = Result.references

print(f"recommendation={recommendation} confidence={confidence} explanation=\"{explanation}\" references='{references}'")
