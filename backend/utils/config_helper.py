import sys
from termcolor import colored
from pydantic import ValidationError


class ConfigHelper():
    def config_color(self, string: str, color: str = "", bold: bool = False):
        """Color the string with the given color and bold attribute.

        Args:
            string (str): The string to color.
            color (str, optional): The color to apply to the string. Defaults to "" --> In this case bold text is returned.
            bold (bool, optional): Whether to apply bold attribute to the string. Defaults to False.

        Returns:
            str: The colored string.
        """
        # If no color provided, default to light_grey with bold
        if not color:
            return colored(string, 'light_grey', attrs=["bold"])

        # If color is provided, only apply bold if explicitly requested
        attrs = ["bold"] if bold else []
        return colored(string, color, attrs=attrs)

    def config_get_user_friendly_error_message(self, error: ValidationError, field_mapping: dict = {}) -> str:
        """Convert Pydantic validation errors to user-friendly messages.

        Args:
            error (ValidationError): The pydantic validation error
            field_mapping (dict): The dict of field mappings that map the variables names within config.py to the environment variable names in the .env file

        Returns:
            str: A string containing all validation error messages
        """
        error_messages = []

        for error_detail in error.errors():
            field_name = error_detail.get(
                "loc", [])[-1] if error_detail.get("loc") else "unknown"
            error_type = error_detail.get("type", "")
            error_msg = error_detail.get("msg", "")

            friendly_field_name = field_mapping.get(
                field_name, field_name.upper())

            # Handle different error types
            if error_type == "missing":
                error_messages.append(
                    f"❌ {self.config_color("Invalid:", "red")} {self.config_color(friendly_field_name)} is required")
            else:
                error_messages.append(
                    f"❌ {self.config_color("Invalid:", "red")} {self.config_color(friendly_field_name)} - {error_msg}")

        return "\n".join(error_messages)

    def validation_handler(self, error, field_mapping):
        error_message = self.config_get_user_friendly_error_message(
            error=error, field_mapping=field_mapping)
        print("\n" + "="*50)
        print(self.config_color("🚨 Configuration Error", "red", bold=True))
        print("="*50)
        print(error_message)
        print(
            f"\n💡 Please check your {self.config_color(".env", "blue")} file and ensure all env variables are set properly.")
        print("="*50)
        sys.exit(1)

    def exception_handler(self, error):
        print("\n" + "="*50)
        print(self.config_color("🚨 Unexpected Error", "red", bold=True))
        print("="*50)
        print(f"An unexpected error occurred: {str(error)}")
        print("="*50)
        sys.exit(1)


helper = ConfigHelper()
