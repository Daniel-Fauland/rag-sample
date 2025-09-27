# fmt: off
import os  # noqa
import sys  # noqa
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.append(os.path.dirname(SCRIPT_DIR))  # noqa

import time  # noqa
import asyncio  # noqa
import asyncpg  # noqa
import subprocess  # noqa
from utils.helper import Utils  # noqa
from config import config  # noqa
# fmt: on


def overwrite_env():
    print("Overwriting certain env variables...")
    backend_dir = os.path.dirname(SCRIPT_DIR)
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{backend_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = backend_dir

    if 'DB_NAME' in env:
        env['DB_NAME'] = f"test_{env['DB_NAME']}"
    else:
        env['DB_NAME'] = config.test_db_name

    env['LOGGING_LEVEL'] = config.test_logging_level
    env['RATE_LIMIT_UNPROTECTED_ROUTES'] = "9999"
    return env


# Drop the test database
async def drop_test_db(env):
    db_test_name = env['DB_NAME']
    conn = await asyncpg.connect(
        user=config.db_user, password=config.db_passwd, database=config.db_name, host=config.db_host
    )
    try:
        # Disconnect other users connected to the test database
        await conn.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_test_name}'
          AND pid <> pg_backend_pid();
        """)
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_test_name
        )
        if db_exists:
            # Drop again to ensure it's gone, and print only if it existed
            await conn.execute(f"DROP DATABASE IF EXISTS {db_test_name};")
            print(f"Test database '{db_test_name}' dropped successfully.")
    finally:
        await conn.close()


# Create the test database
async def create_test_db(env):
    print("Creating test database...")
    db_test_name = env['DB_NAME']
    conn = await asyncpg.connect(
        user=config.db_user, password=config.db_passwd, database=config.db_name, host=config.db_host
    )
    try:
        await conn.execute(f"CREATE DATABASE {db_test_name};")
        print(f"Test database '{db_test_name}' created successfully.")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"Test database '{db_test_name}' already exists.")
    finally:
        await conn.close()

    print("Creating 'alembic_version' table in the test database...")
    conn = await asyncpg.connect(
        user=config.db_user, password=config.db_passwd, database=config.db_name, host=config.db_host
    )
    try:
        await conn.execute("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL);")
    except Exception as e:
        print(f"Error creating 'alembic_version' table: {e}")
    finally:
        await conn.close()


# Run Alembic migrations
async def run_migrations(env, direction="upgrade", revision="head"):
    print(f"Running Alembic migrations: {direction} -> {revision}...")
    subprocess.run(f"alembic {direction} {revision}",
                   shell=True, check=True, text=True, env=env)
    print("Alembic migrations completed.")


# Run the integration tests
def run_tests(env):
    print("Running unit tests...\n")
    try:
        # subprocess.run("ls")
        subprocess.run("pytest -s --color=yes",
                       shell=True, check=True, text=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error when running tests: {e}")
        pass
    print("\nTests completed.")


async def main():
    # Step 0: Start timing for the entire process
    start_time = time.perf_counter()
    history = []

    # Step 1: Overwrite the env variables
    env = overwrite_env()
    history = await helper.timer(start_time, "Environment Setup", history)

    # Step 2: Drop (if exists) and create the test database
    await drop_test_db(env)
    await create_test_db(env)
    history = await helper.timer(start_time, "Provision Test DB", history)

    # Step 3: Run migrations on the test database
    await run_migrations(env, direction="upgrade", revision="head")
    history = await helper.timer(start_time, "Migrations: upgrade -> head", history)

    # Step 4: Run the tests
    run_tests(env)
    history = await helper.timer(start_time, "Integration Tests", history)

    # Step 5: Downgrade the migrations
    await run_migrations(env, direction="downgrade", revision="base")
    history = await helper.timer(start_time, "Migrations: downgrade -> base", history)

    # Step 6: Drop the test database
    await drop_test_db(env)
    history = await helper.timer(start_time, "Delete Test DB", history)

    # Final step: Print output summary using tabulate
    await helper.show_timer_result(history)

# Execute the script
if __name__ == "__main__":
    helper = Utils()
    asyncio.run(main())
