from enum import Enum
from pydantic import BaseModel, Field
from os import getenv
from anthropic import Anthropic
import json

llm_name= "Anthropic"
llm_model = "claude-opus-4-1-20250805"

asset_name="Bitcoin"
prompt = "Provide a recommendation for the asset {asset_name}. Include a buy, sell, or hold recommendation, a confidence level between 0.0 and 1.0, a brief explanation, and any relevant references."

LLM_API_KEY_ID = llm_name + "_API_KEY"
LLM_API_KEY = str(getenv(LLM_API_KEY_ID))

# LLM_BASE_URL_ID = llm_name + "_BASE_URL_ID"
# LLM_BASE_URL = str(getenv(LLM_BASE_URL_ID))

# Initialize Anthropic client
# Use default Anthropic API endpoint (don't use custom base_url for now)
client = Anthropic(
    api_key=LLM_API_KEY
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

def get_asset_recommendation_Anthropic(asset_name: str, prompt: str, model: str) -> AssetRecommendation:
    prompt_asset = prompt.format(asset_name=asset_name)
    
    # Create a structured prompt for Anthropic
    structured_prompt = f"""You are a helpful investment advisor. {prompt_asset}

Please respond with a JSON object in the following format:
{{
    "recommendation": "Buy" | "Sell" | "Hold",
    "confidence": <float between 0.0 and 1.0>,
    "explanation": "<brief explanation>",
    "references": "<references, e.g., 'Wall Street Journal, NY Stock Exchange'>"
}}

Only return the JSON object, no additional text."""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": structured_prompt
                }
            ]
        )
        
        # Extract the response content
        response_text = ""
        for content_block in response.content:
            if content_block.type == 'text':
                response_text += content_block.text
        
        # Parse the JSON response
        response_data = json.loads(response_text)
        
        # Create and return the AssetRecommendation object
        recommendation = AssetRecommendation(
            recommendation=Recommendation(response_data["recommendation"]),
            confidence=response_data["confidence"],
            explanation=response_data["explanation"],
            references=response_data["references"]
        )
        
        return recommendation
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response from Anthropic: {str(e)}")
    except KeyError as e:
        raise Exception(f"Missing required field in Anthropic response: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting recommendation from Anthropic: {str(e)}")

Result = get_asset_recommendation_Anthropic(asset_name, prompt, llm_model)

# Assign the four LLM Query Return values to variables for database storage
recommendation = Result.recommendation.value  # Extract the string value from the enum
confidence = Result.confidence
explanation = Result.explanation
references = Result.references

print(f"recommendation={recommendation} confidence={confidence} explanation=\"{explanation}\" references='{references}'")
