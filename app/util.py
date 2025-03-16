import os

def getPostgresURI():
    user = os.getenv('POSTGRES_USER', '')
    password = os.getenv('POSTGRES_PASSWORD', '')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    dbname = os.getenv('POSTGRES_DB', 'your_default_dbname')

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"