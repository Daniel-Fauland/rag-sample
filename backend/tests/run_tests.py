# fmt: off
import os  # noqa
import sys  # noqa
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.append(os.path.dirname(SCRIPT_DIR))  # noqa

import time  # noqa
import asyncio  # noqa
import subprocess  # noqa
from utils.helper import Utils  # noqa
# fmt: on


def run_tests():
    print("Running unit tests...\n")
    try:
        # Get the backend directory path
        backend_dir = os.path.dirname(SCRIPT_DIR)
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{backend_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = backend_dir

        subprocess.run("ls")
        subprocess.run("pytest -s --color=yes",
                       shell=True, check=True, text=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error when running tests: {e}")
        pass
    print("\nTests completed.")


async def main():
    # Step X-1: Runy any code before the tests
    # TBD

    # Step X: Run the tests
    start_time = time.perf_counter()
    run_tests()
    history = await helper.timer(start_time, "Integration Tests")

    # Step X+1: Run any code after the tests
    # TBD

    # Final step: Print output summary using tabulate
    await helper.show_timer_result(history)

# Execute the script
if __name__ == "__main__":
    helper = Utils()
    asyncio.run(main())
