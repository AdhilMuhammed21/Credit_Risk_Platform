from src.talk_to_data.OpenAI_client import client

SCHEMA = """
Table name: customers

Important columns:

TARGET
- 0 = Non-default
- 1 = Default

AMT_INCOME_TOTAL
AMT_CREDIT
AMT_ANNUITY
CREDIT_INCOME_RATIO
ANNUITY_INCOME_RATIO
DAYS_BIRTH

Rules:
- TARGET is numeric
- Never use text labels like 'defaulter'
"""

PROMPT_TEMPLATE = """
You are a banking risk analyst.

Convert the user's question into a valid SQLite SQL query.

Rules:
- ONLY generate SELECT queries
- DO NOT generate DELETE, UPDATE, INSERT, DROP
- Use table name: customers
- Return ONLY SQL
- Limit results to 100 rows maximum

Schema:
{schema}

Question:
{question}
"""

def generate_sql(question):

    prompt = PROMPT_TEMPLATE.format(
        schema=SCHEMA,
        question=question
    )

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()