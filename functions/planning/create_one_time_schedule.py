import boto3
import json

scheduler = boto3.client('scheduler', endpoint_url='http://localhost:4566')

def create_one_time_schedule(survey_id, execution_time, query_schedule_id, query_type_id, asset_symbol, asset_name, live_prompt_id, forecast_prompt_id, prompt_id, query_type_name):
    scheduler.create_schedule(
        Name=f"crypto-survey-{survey_id}-{query_schedule_id}-one-time",
        ScheduleExpression=f"at({execution_time})",
        GroupName="crypto-forecast-schedules",
        Target={
            'Arn': 'arn:aws:lambda:us-east-1:000000000000:function:forecast-worker',
            'RoleArn': 'arn:aws:iam::000000000000:role/lambda-role',
            'Input': json.dumps({
                'survey_id': survey_id,
                'action': 'run_forecast',
                'query_schedule_id': query_schedule_id,
                'query_type_id': query_type_id,
                'asset_symbol': asset_symbol,
                'asset_name': asset_name,
                'live_prompt_id': live_prompt_id,
                'forecast_prompt_id': forecast_prompt_id,
                'prompt_id': prompt_id,
                'query_type_name': query_type_name
            })
        },
        FlexibleTimeWindow={'Mode': 'OFF'},
        Description=f"One-time forecast for survey ID {survey_id} with query type {query_type_name}"
    )
# paired_query_id
# schedule_id
# scheduled_for_utc

# Example usage
create_one_time_schedule(
    survey_id=123,
    execution_time='2025-09-27T14:00:00',
    query_schedule_id=456,
    query_type_id=789,
    asset_symbol='BTC',
    asset_name='Bitcoin',
    live_prompt_id=101,
    forecast_prompt_id=102,
    prompt_id=103,
    query_type_name='Initial Baseline'
)