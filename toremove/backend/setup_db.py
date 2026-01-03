import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def run_psql_command(command):
    return subprocess.run(
        ["psql", "-U", "postgres", "-h", DB_HOST, "-t", "-A", "-c", command],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def user_exists():
    result = run_psql_command(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}';")
    return result == "1"


def database_exists():
    result = run_psql_command(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
    return result == "1"


def get_database_owner():
    result = run_psql_command(
        f"SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = '{DB_NAME}';"
    )
    return result


def create_database():
    try:
        if not user_exists():
            print(f"Creating user {DB_USER}...")
            subprocess.run(
                [
                    "psql",
                    "-U",
                    "postgres",
                    "-h",
                    DB_HOST,
                    "-c",
                    f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';",
                ],
                check=True,
            )
        else:
            print(f"User {DB_USER} already exists.")

        if not database_exists():
            print(f"Creating database {DB_NAME} with owner {DB_USER}...")
            subprocess.run(
                [
                    "psql",
                    "-U",
                    "postgres",
                    "-h",
                    DB_HOST,
                    "-c",
                    f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};",
                ],
                check=True,
            )
        else:
            owner = get_database_owner()
            if owner != DB_USER:
                print(f"Changing database {DB_NAME} owner from {owner} to {DB_USER}...")
                subprocess.run(
                    [
                        "psql",
                        "-U",
                        "postgres",
                        "-h",
                        DB_HOST,
                        "-c",
                        f"ALTER DATABASE {DB_NAME} OWNER TO {DB_USER};",
                    ],
                    check=True,
                )
            else:
                print(f"Database {DB_NAME} already owned by {DB_USER}.")

        print("Database setup complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    create_database()
