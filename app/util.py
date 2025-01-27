import json

def getPostgresURI():
    # Read json file
    with open("creds/db.json") as f:
        creds = json.load(f)

    user = str(creds["user"])
    password = str(creds["password"])
    host = str(creds["host"])
    port = ":" + str(creds["port"]) if str(creds["port"]) else ""
    database = str(creds["database"])

    return f'postgresql+psycopg2://{user}:{password}@{host}{port}/{database}'
