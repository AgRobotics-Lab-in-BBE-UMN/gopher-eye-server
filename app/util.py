import os

def getPostgresURI():
    user = os.getenv('DB_USER', '')
    password = os.getenv('DB_PASSWORD', '')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    dbname = os.getenv('DB_NAME', '')

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"