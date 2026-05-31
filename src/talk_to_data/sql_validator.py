FORBIDDEN = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER"
]

def validate_sql(query):

    upper_query = query.upper()

    for word in FORBIDDEN:
        if word in upper_query:
            return False

    return True