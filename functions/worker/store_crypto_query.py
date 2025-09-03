import json
import mysql.connector
from datetime import datetime
from typing import Optional
from mysql.connector import Error as MySQLError
from asset_recommendation import get_asset_recommendation_OpenAI, AssetRecommendation

def store_crypto_query(
    db_config: dict,
    asset_name: str,
    survey_id: int,
    schedule_id: int,
    query_type_id: int,
    scheduled_for_utc: datetime,
    target_delay_hours: Optional[int] = None,
    custom_prompt: Optional[str] = None
) -> int:
    """
    Calls get_asset_recommendation_OpenAI, parses the results, and stores them in the crypto_queries table.

    Args:
        db_config (dict): Database connection configuration (host, user, password, database).
        asset_name (str): Name of the asset to query (e.g., 'BTC', 'ETH').
        survey_id (int): ID of the survey (foreign key to surveys table).
        schedule_id (int): ID of the schedule (foreign key to schedules table).
        query_type_id (int): ID of the query type (foreign key to query_type table).
        scheduled_for_utc (datetime): UTC datetime when the query is scheduled.
        target_delay_hours (Optional[int]): Optional target delay in hours.
        custom_prompt (Optional[str]): Optional custom prompt for the OpenAI API.

    Returns:
        int: The query_id of the inserted record.

    Raises:
        ValueError: If required inputs are invalid.
        MySQLError: If database operations fail.
        Exception: For OpenAI API or other unexpected errors.
    """
    if not asset_name or not isinstance(asset_name, str):
        raise ValueError("asset_name must be a non-empty string")
    if not isinstance(survey_id, int) or survey_id <= 0:
        raise ValueError("survey_id must be a positive integer")
    if not isinstance(schedule_id, int) or schedule_id <= 0:
        raise ValueError("schedule_id must be a positive integer")
    if not isinstance(query_type_id, int) or query_type_id <= 0:
        raise ValueError("query_type_id must be a positive integer")
    if not isinstance(scheduled_for_utc, datetime):
        raise ValueError("scheduled_for_utc must be a datetime object")
    if target_delay_hours is not None and (not isinstance(target_delay_hours, int) or target_delay_hours < 0):
        raise ValueError("target_delay_hours must be a non-negative integer or None")

    connection = None
    cursor = None
    query_id = None

    try:
        # Initialize status as RUNNING
        status = 'RUNNING'
        executed_at_utc = datetime.utcnow()

        # Insert initial record with RUNNING status
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO crypto_queries (
                survey_id, schedule_id, query_type_id, target_delay_hours,
                scheduled_for_utc, status, executed_at_utc
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            survey_id, schedule_id, query_type_id, target_delay_hours,
            scheduled_for_utc, status, executed_at_utc
        ))
        connection.commit()
        query_id = cursor.lastrowid

        # Call get_asset_recommendation_OpenAI
        recommendation = get_asset_recommendation_OpenAI(asset_name, custom_prompt)

        # Parse results into JSON
        result_json = {
            "recommendation": recommendation.recommendation.value,
            "confidence": recommendation.confidence,
            "explanation": recommendation.explanation,
            "references": recommendation.references
        }

        # Update record with SUCCEEDED status and results
        update_query = """
            UPDATE crypto_queries
            SET status = %s, result_json = %s, error_text = NULL
            WHERE query_id = %s
        """
        cursor.execute(update_query, ('SUCCEEDED', json.dumps(result_json), query_id))
        connection.commit()

        return query_id

    except MySQLError as db_error:
        # Update record with FAILED status and error message
        if connection and cursor and query_id:
            update_query = """
                UPDATE crypto_queries
                SET status = %s, error_text = %s
                WHERE query_id = %s
            """
            cursor.execute(update_query, ('FAILED', str(db_error), query_id))
            connection.commit()
        raise MySQLError(f"Database error: {str(db_error)}")

    except Exception as e:
        # Update record with FAILED status and error message
        if connection and cursor and query_id:
            update_query = """
                UPDATE crypto_queries
                SET status = %s, error_text = %s
                WHERE query_id = %s
            """
            cursor.execute(update_query, ('FAILED', str(e), query_id))
            connection.commit()
        raise Exception(f"Error processing query: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Example usage
if __name__ == "__main__":
    db_config = {
        "host": "localhost",
        "user": "your_username",
        "password": "your_password",
        "database": "your_database"
    }
    try:
        query_id = store_crypto_query(
            db_config=db_config,
            asset_name="BTC",
            survey_id=1,
            schedule_id=1,
            query_type_id=1,
            scheduled_for_utc=datetime.utcnow(),
            target_delay_hours=24
        )
        print(f"Query stored successfully with query_id: {query_id}")
    except Exception as e:
        print(f"Error: {e}")