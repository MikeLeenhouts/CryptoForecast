#!/usr/bin/env python3
"""
Test script for validating the get_asset_recommendation_OpenAI function.
This script tests various scenarios including valid inputs, edge cases, and error handling.
"""

import os
import sys
import json
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Add the current directory to Python path to import the function
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from get_asset_recommendation_OpenAI import (
        get_asset_recommendation_OpenAI, 
        AssetRecommendation, 
        Recommendation
    )
    print("✅ Successfully imported the function and models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_syntax_validation():
    """Test basic syntax and model validation"""
    print("\n🔍 Testing Syntax and Model Validation...")
    
    try:
        # Test Pydantic model creation
        test_recommendation = AssetRecommendation(
            recommendation=Recommendation.BUY,
            confidence=0.85,
            explanation="Test explanation",
            references="Test references"
        )
        print("✅ Pydantic model creation successful")
        print(f"   Model: {test_recommendation}")
        
        # Test enum values
        for rec in Recommendation:
            print(f"   Enum value: {rec.name} = {rec.value}")
        
        return True
    except Exception as e:
        print(f"❌ Syntax validation failed: {e}")
        return False

def test_input_validation():
    """Test input validation and error handling"""
    print("\n🔍 Testing Input Validation...")
    
    test_cases = [
        ("", "Empty string should raise ValueError"),
        (None, "None should raise ValueError"),
        (123, "Non-string should raise ValueError"),
        ("   ", "Whitespace-only should raise ValueError"),
    ]
    
    for test_input, description in test_cases:
        try:
            get_asset_recommendation_OpenAI(test_input)
            print(f"❌ {description} - but no error was raised")
        except ValueError as e:
            print(f"✅ {description} - correctly raised ValueError: {e}")
        except Exception as e:
            print(f"⚠️  {description} - raised unexpected error: {e}")

def test_with_mock_openai():
    """Test function with mocked OpenAI responses"""
    print("\n🔍 Testing with Mocked OpenAI Responses...")
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.parsed = AssetRecommendation(
        recommendation=Recommendation.BUY,
        confidence=0.75,
        explanation="Strong fundamentals and positive market sentiment",
        references="Financial Times, Bloomberg"
    )
    
    with patch('get_asset_recommendation_OpenAI.client.chat.completions.create') as mock_create:
        mock_create.return_value = mock_response
        
        try:
            result = get_asset_recommendation_OpenAI("AAPL")
            print("✅ Mock test successful")
            print(f"   Recommendation: {result.recommendation.value}")
            print(f"   Confidence: {result.confidence}")
            print(f"   Explanation: {result.explanation}")
            print(f"   References: {result.references}")
            return True
        except Exception as e:
            print(f"❌ Mock test failed: {e}")
            return False

def test_with_custom_prompt():
    """Test function with custom prompt using mock"""
    print("\n🔍 Testing Custom Prompt...")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.parsed = AssetRecommendation(
        recommendation=Recommendation.HOLD,
        confidence=0.60,
        explanation="Market uncertainty suggests waiting",
        references="Reuters, MarketWatch"
    )
    
    custom_prompt = "Analyze Tesla stock considering recent earnings and market conditions"
    
    with patch('get_asset_recommendation_OpenAI.client.chat.completions.create') as mock_create:
        mock_create.return_value = mock_response
        
        try:
            result = get_asset_recommendation_OpenAI("TSLA", custom_prompt)
            print("✅ Custom prompt test successful")
            print(f"   Used custom prompt: {custom_prompt}")
            print(f"   Result: {result.recommendation.value} with {result.confidence} confidence")
            
            # Verify the mock was called with correct parameters
            call_args = mock_create.call_args
            messages = call_args[1]['messages']
            assert messages[1]['content'] == custom_prompt
            print("✅ Custom prompt was correctly passed to OpenAI")
            return True
        except Exception as e:
            print(f"❌ Custom prompt test failed: {e}")
            return False

def test_openai_api_error_handling():
    """Test error handling for OpenAI API failures"""
    print("\n🔍 Testing OpenAI API Error Handling...")
    
    with patch('get_asset_recommendation_OpenAI.client.chat.completions.create') as mock_create:
        # Simulate API error
        mock_create.side_effect = Exception("API rate limit exceeded")
        
        try:
            get_asset_recommendation_OpenAI("AAPL")
            print("❌ Should have raised an exception for API error")
            return False
        except Exception as e:
            if "Error getting recommendation from OpenAI" in str(e):
                print("✅ API error correctly handled and wrapped")
                return True
            else:
                print(f"❌ Unexpected error format: {e}")
                return False

def test_real_openai_call():
    """Test with real OpenAI API call (if API key is available)"""
    print("\n🔍 Testing Real OpenAI API Call...")
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("   Skipping real API test. To test with real API:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return True
    
    try:
        print("   Making real API call to OpenAI...")
        result = get_asset_recommendation_OpenAI("AAPL")
        
        print("✅ Real API call successful!")
        print(f"   Asset: AAPL")
        print(f"   Recommendation: {result.recommendation.value}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Explanation: {result.explanation}")
        print(f"   References: {result.references}")
        
        # Validate the response structure
        assert isinstance(result.recommendation, Recommendation)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.explanation, str) and len(result.explanation) > 0
        assert isinstance(result.references, str) and len(result.references) > 0
        
        print("✅ Response validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Real API call failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("🚀 Starting Validation Tests for get_asset_recommendation_OpenAI")
    print("=" * 70)
    
    tests = [
        test_syntax_validation,
        test_input_validation,
        test_with_mock_openai,
        test_with_custom_prompt,
        test_openai_api_error_handling,
        test_real_openai_call
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The function appears to be working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
