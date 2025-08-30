# Basic GET Queries - Quick Test Reference

This document provides a comprehensive list of basic GET queries for all endpoints in the Crypto Forecasts API. Use these for quick testing and verification of the API functionality.

## Base URL
```
http://localhost:8080
```

## Health Check
```bash
# Health check endpoint
curl -X GET "http://localhost:8080/healthz"
# Direct URL: http://localhost:8080/healthz
```

## CRUD Endpoints - Basic List Operations

### 1. Asset Types
```bash
# List all asset types
curl -X GET "http://localhost:8080/asset-types"
# Direct URL: http://localhost:8080/asset-types

# Get specific asset type (replace {id} with actual ID)
curl -X GET "http://localhost:8080/asset-types/{id}"
# Direct URL: http://localhost:8080/asset-types/1
```

### 2. Assets
```bash
# List all assets
curl -X GET "http://localhost:8080/assets"
# Direct URL: http://localhost:8080/assets

# Get specific asset
curl -X GET "http://localhost:8080/assets/{id}"
# Direct URL: http://localhost:8080/assets/1

# Filter assets by asset_type_id
curl -X GET "http://localhost:8080/assets?asset_type_id=1"
# Direct URL: http://localhost:8080/assets?asset_type_id=1
```

### 3. LLMs (Large Language Models)
```bash
# List all LLMs
curl -X GET "http://localhost:8080/llms"
# Direct URL: http://localhost:8080/llms

# Get specific LLM
curl -X GET "http://localhost:8080/llms/{id}"
# Direct URL: http://localhost:8080/llms/1
```

### 4. Prompts
```bash
# List all prompts
curl -X GET "http://localhost:8080/prompts"
# Direct URL: http://localhost:8080/prompts

# Get specific prompt
curl -X GET "http://localhost:8080/prompts/{id}"
# Direct URL: http://localhost:8080/prompts/1

# Filter prompts by LLM ID
curl -X GET "http://localhost:8080/prompts?llm_id=1"
# Direct URL: http://localhost:8080/prompts?llm_id=1

# Filter prompts by version
curl -X GET "http://localhost:8080/prompts?prompt_version=1.0"
# Direct URL: http://localhost:8080/prompts?prompt_version=1.0
```

### 5. Schedules
```bash
# List all schedules
curl -X GET "http://localhost:8080/schedules"
# Direct URL: http://localhost:8080/schedules

# Get specific schedule
curl -X GET "http://localhost:8080/schedules/{id}"
# Direct URL: http://localhost:8080/schedules/1
```

### 6. Query Types
```bash
# List all query types
curl -X GET "http://localhost:8080/query-types"
# Direct URL: http://localhost:8080/query-types

# Get specific query type
curl -X GET "http://localhost:8080/query-types/{id}"
# Direct URL: http://localhost:8080/query-types/1
```

### 7. Query Schedules
```bash
# List all query schedules
curl -X GET "http://localhost:8080/query-schedules"
# Direct URL: http://localhost:8080/query-schedules

# Get specific query schedule
curl -X GET "http://localhost:8080/query-schedules/{id}"
# Direct URL: http://localhost:8080/query-schedules/1

# Filter by schedule ID
curl -X GET "http://localhost:8080/query-schedules?schedule_id=1"
# Direct URL: http://localhost:8080/query-schedules?schedule_id=1
```

### 8. Surveys
```bash
# List all surveys
curl -X GET "http://localhost:8080/surveys"
# Direct URL: http://localhost:8080/surveys

# Get specific survey
curl -X GET "http://localhost:8080/surveys/{id}"
# Direct URL: http://localhost:8080/surveys/1

# Filter surveys by asset ID
curl -X GET "http://localhost:8080/surveys?asset_id=1"
# Direct URL: http://localhost:8080/surveys?asset_id=1

# Filter surveys by schedule ID
curl -X GET "http://localhost:8080/surveys?schedule_id=1"
# Direct URL: http://localhost:8080/surveys?schedule_id=1

# Filter surveys by prompt ID
curl -X GET "http://localhost:8080/surveys?prompt_id=1"
# Direct URL: http://localhost:8080/surveys?prompt_id=1

# Filter surveys by active status
curl -X GET "http://localhost:8080/surveys?is_active=true"
# Direct URL: http://localhost:8080/surveys?is_active=true

curl -X GET "http://localhost:8080/surveys?is_active=false"
# Direct URL: http://localhost:8080/surveys?is_active=false
```

### 9. Crypto Queries
```bash
# List all crypto queries
curl -X GET "http://localhost:8080/crypto-queries"
# Direct URL: http://localhost:8080/crypto-queries

# Get specific crypto query
curl -X GET "http://localhost:8080/crypto-queries/{id}"
# Direct URL: http://localhost:8080/crypto-queries/1

# Filter by survey ID
curl -X GET "http://localhost:8080/crypto-queries?survey_id=1"
# Direct URL: http://localhost:8080/crypto-queries?survey_id=1

# Filter by schedule ID
curl -X GET "http://localhost:8080/crypto-queries?schedule_id=1"
# Direct URL: http://localhost:8080/crypto-queries?schedule_id=1

# Filter by query type ID
curl -X GET "http://localhost:8080/crypto-queries?query_type_id=1"
# Direct URL: http://localhost:8080/crypto-queries?query_type_id=1

# Filter by status
curl -X GET "http://localhost:8080/crypto-queries?status=SUCCEEDED"
# Direct URL: http://localhost:8080/crypto-queries?status=SUCCEEDED

curl -X GET "http://localhost:8080/crypto-queries?status=PLANNED"
# Direct URL: http://localhost:8080/crypto-queries?status=PLANNED

curl -X GET "http://localhost:8080/crypto-queries?status=RUNNING"
# Direct URL: http://localhost:8080/crypto-queries?status=RUNNING

curl -X GET "http://localhost:8080/crypto-queries?status=FAILED"
# Direct URL: http://localhost:8080/crypto-queries?status=FAILED

curl -X GET "http://localhost:8080/crypto-queries?status=CANCELLED"
# Direct URL: http://localhost:8080/crypto-queries?status=CANCELLED
```

### 10. Crypto Forecasts
```bash
# List all crypto forecasts
curl -X GET "http://localhost:8080/crypto-forecasts"
# Direct URL: http://localhost:8080/crypto-forecasts

# Get specific crypto forecast
curl -X GET "http://localhost:8080/crypto-forecasts/{id}"
# Direct URL: http://localhost:8080/crypto-forecasts/1

# Filter by query ID
curl -X GET "http://localhost:8080/crypto-forecasts?query_id=1"
# Direct URL: http://localhost:8080/crypto-forecasts?query_id=1

# Filter by horizon type
curl -X GET "http://localhost:8080/crypto-forecasts?horizon_type=1_hour"
# Direct URL: http://localhost:8080/crypto-forecasts?horizon_type=1_hour

curl -X GET "http://localhost:8080/crypto-forecasts?horizon_type=1_day"
# Direct URL: http://localhost:8080/crypto-forecasts?horizon_type=1_day

curl -X GET "http://localhost:8080/crypto-forecasts?horizon_type=1_week"
# Direct URL: http://localhost:8080/crypto-forecasts?horizon_type=1_week
```

## Provisioning Endpoints (Additional Survey Operations)

### Survey Operations
```bash
# List surveys (provisioning endpoint)
curl -X GET "http://localhost:8080/surveys"
# Direct URL: http://localhost:8080/surveys

# Get specific survey (provisioning endpoint)
curl -X GET "http://localhost:8080/surveys/{id}"
# Direct URL: http://localhost:8080/surveys/1

# Filter surveys by asset ID (provisioning)
curl -X GET "http://localhost:8080/surveys?asset_id=1"
# Direct URL: http://localhost:8080/surveys?asset_id=1

# Filter surveys by active status (provisioning)
curl -X GET "http://localhost:8080/surveys?is_active=true"
# Direct URL: http://localhost:8080/surveys?is_active=true
```

## Reporting Endpoints

### Survey Reports
```bash
# Get survey runs report
curl -X GET "http://localhost:8080/reports/surveys/{survey_id}/runs"
# Direct URL: http://localhost:8080/reports/surveys/1/runs

# Get survey comparison report
curl -X GET "http://localhost:8080/reports/surveys/{survey_id}/comparison"
# Direct URL: http://localhost:8080/reports/surveys/1/comparison
```

## API Documentation
```bash
# OpenAPI/Swagger documentation
curl -X GET "http://localhost:8080/docs"
# Direct URL: http://localhost:8080/docs

# OpenAPI JSON schema
curl -X GET "http://localhost:8080/openapi.json"
# Direct URL: http://localhost:8080/openapi.json
```

## Quick Test Sequence

Here's a recommended sequence for testing all basic endpoints:

```bash
# 1. Health check
curl -X GET "http://localhost:8080/healthz"

# 2. Test all basic list endpoints
curl -X GET "http://localhost:8080/asset-types"
curl -X GET "http://localhost:8080/assets"
curl -X GET "http://localhost:8080/llms"
curl -X GET "http://localhost:8080/prompts"
curl -X GET "http://localhost:8080/schedules"
curl -X GET "http://localhost:8080/query-types"
curl -X GET "http://localhost:8080/query-schedules"
curl -X GET "http://localhost:8080/surveys"
curl -X GET "http://localhost:8080/crypto-queries"
curl -X GET "http://localhost:8080/crypto-forecasts"

# 3. Test documentation endpoints
curl -X GET "http://localhost:8080/docs"
curl -X GET "http://localhost:8080/openapi.json"
```

## Notes

- Replace `{id}` with actual numeric IDs when testing specific item endpoints
- Replace `{survey_id}` with actual survey IDs when testing reporting endpoints
- All endpoints return JSON responses
- Use the Swagger UI at `http://localhost:8080/docs` for interactive testing
- Filter parameters are optional and can be combined where supported
- Status values for crypto queries: PLANNED, RUNNING, SUCCEEDED, FAILED, CANCELLED
- Common horizon types: 1_hour, 1_day, 1_week, 1_month, etc.
