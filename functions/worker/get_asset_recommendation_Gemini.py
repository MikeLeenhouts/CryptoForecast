import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from enum import Enum
from pydantic import BaseModel, Field
from os import getenv
import re
import json
import time

llm_name = "Gemini"
llm_model = "gemini-1.5-pro"  # Stable model as of Sep 2025 (verify at https://ai.google.dev)

asset_name = "Bitcoin"
prompt = "Provide a recommendation for the asset {asset_name}. Include a buy, sell, or hold recommendation, a confidence level between 0.0 and 1.0, a brief explanation, and any relevant references. Format the response as a JSON object with fields: recommendation (string: 'Buy', 'Sell', 'Hold'), confidence (float, 0.0-1.0), explanation (string), references (string). Return only the JSON object, enclosed in triple backticks (```), with no additional text or markdown."

LLM_API_KEY_ID = llm_name + "_API_KEY"
LLM_API_KEY = str(getenv(LLM_API_KEY_ID))
if not LLM_API_KEY or LLM_API_KEY == "None":
    raise ValueError(f"Missing or invalid {LLM_API_KEY_ID} environment variable. Set it to your Gemini API key.")

# Debug API key (avoid logging full key in production)
print(f"Environment variable name: {LLM_API_KEY_ID}")
print(f"API key exists: {LLM_API_KEY is not None}")
print(f"API key length: {len(LLM_API_KEY) if LLM_API_KEY else 0}")
print(f"First 10 chars: {LLM_API_KEY[:10] if LLM_API_KEY and len(LLM_API_KEY) >= 10 else 'N/A'}")

# Clean the API key
if LLM_API_KEY:
    LLM_API_KEY = LLM_API_KEY.strip()

# Initialize Gemini client
genai.configure(api_key=LLM_API_KEY)
client = genai.GenerativeModel(model_name=llm_model)

class Recommendation(Enum):
    BUY = "Buy"
    SELL = "Sell"
    HOLD = "Hold"

class AssetRecommendation(BaseModel):
    recommendation: Recommendation = Field(..., description="Recommendation: Buy, Sell, or Hold")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level between 0.0 and 1.0")
    explanation: str = Field(..., description="Brief explanation of why")
    references: str = Field(..., description="References, e.g., 'Wall Street Journal, NY Stock Exchange'")

def parse_gemini_response(text: str) -> AssetRecommendation:
    """Parse Gemini's text response into AssetRecommendation."""
    try:
        # Try to extract JSON with multiple patterns
        json_str = None
        
        # Pattern 1: ```json\n{...}\n```
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Pattern 2: ```{...}```
            json_match = re.search(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Pattern 3: Plain JSON object
                json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
        
        if json_str:
            data = json.loads(json_str)
            return AssetRecommendation(
                recommendation=data["recommendation"],
                confidence=data["confidence"],
                explanation=data["explanation"],
                references=data["references"]
            )
        else:
            # Fallback: Parse text manually
            lines = text.splitlines()
            recommendation = confidence = explanation = references = None
            explanation_lines = []
            capture_explanation = False
            for line in lines:
                line = line.strip()
                if line.startswith("Recommendation:"):
                    recommendation = line.split(":", 1)[1].strip().capitalize()
                elif line.startswith("Confidence:"):
                    confidence = float(line.split(":", 1)[1].strip())
                elif line.startswith("Explanation:"):
                    capture_explanation = True
                    explanation_lines.append(line.split(":", 1)[1].strip())
                elif line.startswith("References:"):
                    capture_explanation = False
                    references = line.split(":", 1)[1].strip()
                elif capture_explanation and line:
                    explanation_lines.append(line)
            explanation = " ".join(explanation_lines).strip()
            if all([recommendation, confidence, explanation, references]):
                return AssetRecommendation(
                    recommendation=recommendation,
                    confidence=confidence,
                    explanation=explanation,
                    references=references
                )
            raise ValueError(f"Could not parse response: {text[:200]}...")
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response: {str(e)}")

def get_asset_recommendation_Gemini(asset_name: str, prompt: str, model: str, max_retries: int = 3) -> AssetRecommendation:
    prompt_asset = prompt.format(asset_name=asset_name)
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Calling Gemini API with model {model}")
            response = client.generate_content(prompt_asset)
            if not response.candidates or not response.candidates[0].content.parts:
                raise ValueError("Empty response from Gemini")
            text = response.candidates[0].content.parts[0].text
            print(f"Raw response: {text[:200]}...")  # Debug print
            recommendation = parse_gemini_response(text)
            return recommendation
        except GoogleAPIError as e:
            if "404" in str(e) or "model not found" in str(e).lower():
                print(f"404 or invalid model error on attempt {attempt + 1}: Check model '{model}' at https://ai.google.dev.")
                if attempt < max_retries - 1:
                    print("Retrying with delay...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            raise Exception(f"Gemini API error: {str(e)}")
        except ValueError as e:
            print(f"Parsing error on attempt {attempt + 1}: {str(e)[:200]}...")
            if attempt < max_retries - 1:
                print("Retrying with delay...")
                time.sleep(2 ** attempt)
                continue
            raise Exception(f"Error parsing Gemini response after {max_retries} attempts: {str(e)}")
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {str(e)[:200]}...")
            if attempt < max_retries - 1:
                print("Retrying with delay...")
                time.sleep(2 ** attempt)
                continue
            raise Exception(f"Error getting recommendation from Gemini after {max_retries} attempts: {str(e)}")

Result = get_asset_recommendation_Gemini(asset_name, prompt, llm_model)

# Assign the four LLM Query Return values to variables for database storage
recommendation = Result.recommendation.value  # Extract the string value from the enum
confidence = Result.confidence
explanation = Result.explanation
references = Result.references

print(f"recommendation={recommendation} confidence={confidence} explanation=\"{explanation}\" references='{references}'")
