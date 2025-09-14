import time
import subprocess
from fastapi.concurrency import run_in_threadpool
from tabulate import tabulate
from utils.config_helper import helper
from config import config


class Utils():
    @staticmethod
    async def color(string: str, color: str = "", bold: bool = False):
        """Color the string with the given color and bold attribute.

        Args:
            string (str): The string to color.
            color (str, optional): The color to apply to the string. Defaults to "" --> In this case bold text is returned.
            bold (bool, optional): Whether to apply bold attribute to the string. Defaults to False.

        Returns:
            str: The colored string.
        """
        # If env var is_local is False do not color the string
        if not config.is_local:
            return string
        # Offload synchronous function to a new worker thread
        return await run_in_threadpool(helper.config_color, string, color, bold)

    @staticmethod
    async def file_to_str(file_path):
        """
        Reads the contents of a file (e.g. .txt or .md) and returns it as a string.

        Args:
            file_path (str): The path to a file.

        Returns:
            str: Contents of the file as a string, or None if an error occurs.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at path: {file_path}")
        except Exception as e:
            raise e

    @staticmethod
    async def is_truthy(value: str) -> bool:
        """Determine if a string represents a truthy value.

        Args:
            value (str): Any string.

        Returns:
            bool: A boolean value indicating if the string is truthy.
        """
        false_values = {"false", "0", ""}
        return value.lower() not in false_values

    @staticmethod
    async def run_command(command: str, shell: bool = True, check: bool = True, text: bool = False) -> str:
        """Run a command in the shell using subprocess and return the output.

        Args:
            command (str): The command to run.
            shell (bool, optional): Defaults to True.
            check (bool, optional): Defaults to True.

        Returns:
            str: The result of the command.
        """
        try:
            output = subprocess.run(
                command,
                shell=shell,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text
            )
            if text:
                return output.stdout.strip()
            return output.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            return f"Error occurred:\n{e.stdout.strip()}\n{e.stderr.strip()}\n"

    @staticmethod
    async def timer(start_time: float, title: str, history: list[dict] = []) -> list[dict]:
        """Measure the time between a start_time and now add it to a list of dicts and return this list

        Args:
            start_time (float): The initial start time using time.perf_counter() (only needed for the first call)
            title (str): A name for the process you want to time
            history (list[dict], optional): An existing history of times. Defaults to [].

        Returns:
            list[dict]: The updated history
        """
        current_time = time.perf_counter()

        if history:
            # Calculate total time of all previous steps
            total_previous_time = sum(
                step["Processing time"] for step in history)
            # Step duration = current elapsed time - previous total time
            step_duration = round(
                (current_time - start_time) - total_previous_time, 2)
        else:
            # First step: just calculate from start_time
            step_duration = round(current_time - start_time, 2)

        history.append({"Step": title, "Processing time": step_duration})
        return history

    @staticmethod
    async def show_timer_result(history: list[dict]):
        """Show a structured output regarding the duration of the tasks using tabulate

        Args:
            history (list[dict]): The history of processing times
        """
        if len(history) > 1:
            total_duration = round(sum(item.get("Processing time", 0)
                                       for item in history), 2)
            history.append({"Step": "Total Duration",
                            "Processing time": total_duration})
        # Add "s" to the "Processing time" values for display
        for item in history:
            if "Processing time" in item:
                item["Processing time"] = f"{item['Processing time']}s"
        print(tabulate(history, headers='keys', tablefmt='rounded_outline'))


# Initiate for quick access
color = Utils.color
