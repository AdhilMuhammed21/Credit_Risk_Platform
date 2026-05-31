from src.talk_to_data.sql_generator import generate_sql

question = "What is the average income of defaulters?"

sql = generate_sql(question)

print(sql)