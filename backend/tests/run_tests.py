# fmt: off
import os  # noqa
import sys  # noqa
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.append(os.path.dirname(SCRIPT_DIR))  # noqa

import time  # noqa
import asyncio  # noqa
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

    env['LOGGING_LEVEL'] = config.test_logging_level
    # overwrite more env variables here...
    return env

# def run_tests():
#     print("Running unit tests...\n")
#     try:
#         # Get the backend directory path
#         backend_dir = os.path.dirname(SCRIPT_DIR)
#         env = os.environ.copy()
#         if 'PYTHONPATH' in env:
#             env['PYTHONPATH'] = f"{backend_dir}:{env['PYTHONPATH']}"
#         else:
#             env['PYTHONPATH'] = backend_dir

#         subprocess.run("ls")
#         subprocess.run("pytest -s --color=yes",
#                        shell=True, check=True, text=True, env=env)
#     except subprocess.CalledProcessError as e:
#         print(f"Error when running tests: {e}")
#         pass
#     print("\nTests completed.")


# Run the integration tests
def run_tests(env, test_path=None):
    if test_path:
        print(f"Running unit tests for: {test_path}\n")
        pytest_cmd = f"pytest -s --color=yes {test_path}"
    else:
        print("Running unit tests...\n")
        pytest_cmd = "pytest -s --color=yes"

    try:
        # subprocess.run("ls")
        subprocess.run(pytest_cmd,
                       shell=True, check=True, text=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error when running tests: {e}")
        pass
    print("\nTests completed.")


async def main():
    # Step 0: Start timing for the entire process
    start_time = time.perf_counter()
    history = []
    # Parse command-line arguments for test path
    test_path = None
    if len(sys.argv) > 1:
        test_path = sys.argv[1]

    # Step 1: Overwrite the env variables
    env = overwrite_env()
    history = await helper.timer(start_time, "Environment Setup", history)

    # Step X-1: Runy any code before the tests
    # TBD

    # Step X: Run the tests
    run_tests(env=env, test_path=test_path)
    history = await helper.timer(start_time, "Integration Tests", history)

    # Step X+1: Run any code after the tests
    # TBD

    # Final step: Print output summary using tabulate
    await helper.show_timer_result(history)

# Execute the script
if __name__ == "__main__":
    helper = Utils()
    asyncio.run(main())
