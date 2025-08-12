import subprocess
from fastapi.concurrency import run_in_threadpool
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
    def color_sync(string: str, color: str = "", bold: bool = False):
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
        return helper.config_color(string=string, color=color, bold=bold)

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


# Initiate for quick access
color = Utils.color
color_sync = Utils.color_sync
