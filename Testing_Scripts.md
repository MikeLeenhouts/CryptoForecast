# Complete Test Case Inventory and API Endpoint Documentation

## Container Status

✅ __MySQL Container__: Running healthy on port 3306 
✅ __API Container__: Running successfully on port 8080 
✅ __Base URL__: [](http://localhost:8080)<http://localhost:8080> 
✅ __API Documentation__: [](http://localhost:8080/docs)<http://localhost:8080/docs>


## Test Cases Inventory

### 1. Asset Types Tests (`test_asset_types.py`)

__Test Function__: `test_asset_types_crud` __API Endpoints__:

- `POST /asset-types` - Create asset type
- `GET /asset-types/{id}` - Get asset type by ID
- `GET /asset-types?kwargs=` - List all asset types
- `PATCH /asset-types/{id}` - Update asset type
- `DELETE /asset-types/{id}` - Delete asset type

__Execute Test__: `docker-compose exec api python -m pytest tests/test_asset_types.py -v`

### 2. Assets Tests (`test_assets.py`)

__Test Function__: `test_assets_crud_with_fk` __API Endpoints__:

- `POST /assets` - Create asset (requires asset_type_id)
- `GET /assets?asset_type_id={id}` - List assets by type
- `PATCH /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset

__Execute Test__: `docker-compose exec api python -m pytest tests/test_assets.py -v`

### 3. LLMs Tests (`test_llms.py`)

__Test Function__: `test_llms_crud` __API Endpoints__:

- `POST /llms` - Create LLM configuration
- `GET /llms/{id}` - Get LLM by ID
- `GET /llms?kwargs=` - List all LLMs
- `GET /llms?name={name}` - Filter LLMs by name
- `PATCH /llms/{id}` - Update LLM
- `DELETE /llms/{id}` - Delete LLM

__Execute Test__: `docker-compose exec api python -m pytest tests/test_llms.py -v`

### 4. Prompts Tests (`test_prompts.py`)

__Test Function__: `test_prompts_crud_with_fk` __API Endpoints__:

- `POST /prompts` - Create prompt (requires llm_id)
- `GET /prompts/{id}` - Get prompt by ID
- `GET /prompts?kwargs=` - List all prompts
- `GET /prompts?llm_id={id}` - Filter prompts by LLM
- `PATCH /prompts/{id}` - Update prompt
- `DELETE /prompts/{id}` - Delete prompt

__Execute Test__: `docker-compose exec api python -m pytest tests/test_prompts.py -v`

### 5. Schedules Tests (`test_schedules.py`)

__Test Function__: `test_schedules_crud_with_fk` __API Endpoints__:

- `POST /schedules` - Create schedule
- `GET /schedules/{id}` - Get schedule by ID
- `GET /schedules?kwargs=` - List all schedules
- `PATCH /schedules/{id}` - Update schedule
- `DELETE /schedules/{id}` - Delete schedule

__Execute Test__: `docker-compose exec api python -m pytest tests/test_schedules.py -v`

### 6. Schedule Followups Tests (`test_schedule_followups.py`)

__Test Function__: `test_schedule_followups_crud_with_fk` __API Endpoints__:

- `POST /schedule-followups` - Create schedule followup (requires schedule_id)
- `GET /schedule-followups/{id}` - Get followup by ID
- `GET /schedule-followups?kwargs=` - List all followups
- `GET /schedule-followups?schedule_id={id}` - Filter by schedule
- `PATCH /schedule-followups/{id}` - Update followup
- `DELETE /schedule-followups/{id}` - Delete followup

__Execute Test__: `docker-compose exec api python -m pytest tests/test_schedule_followups.py -v`

### 7. Surveys Tests (`test_surveys.py`)

__Test Function__: `test_surveys_crud` __API Endpoints__:

- `POST /surveys` - Create survey
- `GET /surveys/{id}` - Get survey by ID
- `GET /surveys?kwargs=` - List all surveys
- `GET /surveys?name={name}` - Filter surveys by name
- `GET /surveys?is_active={true/false}` - Filter by active status
- `PATCH /surveys/{id}` - Update survey
- `DELETE /surveys/{id}` - Delete survey

__Execute Test__: `docker-compose exec api python -m pytest tests/test_surveys.py -v`

### 8. Queries Tests (`test_crypto_queries.py`)

__Test Function__: `test_crypto_queries_crud_with_fks` __API Endpoints__:

- `POST /queries` - Create crypto query (requires survey_id, asset_id)
- `GET /queries/{id}` - Get query by ID
- `GET /queries?kwargs=` - List all queries
- `GET /queries?survey_id={id}` - Filter by survey
- `GET /queries?asset_id={id}` - Filter by asset
- `PATCH /queries/{id}` - Update query
- `DELETE /queries/{id}` - Delete query

__Execute Test__: `docker-compose exec api python -m pytest tests/test_crypto_queries.py -v`

### 9. Crypto Forecasts Tests (`test_crypto_forecasts.py`)

__Test Function__: `test_schedule_followups_crud_with_fk` __API Endpoints__:

- `POST /crypto-forecasts` - Create forecast (requires query_id)
- `GET /crypto-forecasts/{id}` - Get forecast by ID
- `GET /crypto-forecasts?kwargs=` - List all forecasts
- `GET /crypto-forecasts?query_id={id}` - Filter by query
- `GET /crypto-forecasts?horizon_type={type}` - Filter by horizon
- `PATCH /crypto-forecasts/{id}` - Update forecast
- `DELETE /crypto-forecasts/{id}` - Delete forecast

__Execute Test__: `docker-compose exec api python -m pytest tests/test_crypto_forecasts.py -v`

### 10. Reports Tests (`test_reports.py`)

__Test Function__: `test_survey_reports_flow` __API Endpoints__:

- `GET /reports/surveys/{survey_id}/runs` - Get survey run reports
- `GET /reports/surveys/{survey_id}/comparison` - Get survey comparison reports

__Execute Test__: `docker-compose exec api python -m pytest tests/test_reports.py -v`

## Additional Provisioning Endpoints

- `PATCH /surveys/{survey_id}/activate` - Activate survey
- `PATCH /surveys/{survey_id}/deactivate` - Deactivate survey
- `POST /surveys/{survey_id}/queries/initial` - Create initial query
- `POST /surveys/{survey_id}/queries/followup` - Create followup query

## Execute All Tests

__Run All Tests__: `docker-compose exec api python -m pytest tests/ -v` __Run Specific Test File__: `docker-compose exec api python -m pytest tests/test_{filename}.py -v`

## Manual API Testing Examples

```bash
# Test health endpoint
curl http://localhost:8080/healthz

# Create asset type
curl -X POST http://localhost:8080/asset-types \
  -H "Content-Type: application/json" \
  -d '{"asset_type_name": "TestCrypto", "description": "Test asset type"}'

# List asset types
curl "http://localhost:8080/asset-types?kwargs="

# View API documentation
curl http://localhost:8080/docs
```
