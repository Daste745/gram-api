from os import getenv


def db_connection_string() -> str:
    """
    Takes database connection settings from the environment
    and compiles them into a postgres connection string.
    """
    user = getenv("POSTGRES_USER")
    password = getenv("POSTGRES_PASSWORD")
    host = getenv("POSTGRES_HOST")
    port = getenv("POSTGRES_PORT")
    database = getenv("POSTGRES_DB")
    return f"postgres://{user}:{password}@{host}:{port}/{database}"


def redis_connection_string() -> str:
    host = getenv("REDIS_HOST")
    return f"redis://{host}"
