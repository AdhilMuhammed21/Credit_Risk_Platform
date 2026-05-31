from src.talk_to_data.sql_generator import generate_sql
from src.talk_to_data.sql_validator import validate_sql
from src.talk_to_data.query_executor import run_query


def ask(question):

    sql = generate_sql(question)

    if not validate_sql(sql):

        return {
            "sql": sql,
            "result": "Unsafe query blocked."
        }

    try:

        result = run_query(sql)

        return {
            "sql": sql,
            "result": result
        }

    except Exception as e:

        return {
            "sql": sql,
            "result": f"Query failed: {e}"
        }