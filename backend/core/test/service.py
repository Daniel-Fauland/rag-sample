import re
from utils.logging import logger
from utils.helper import color


class TestService:
    async def convert_string(self, message: str, conversion_type: str):
        async def to_camel_case(s: str) -> str:
            words = s.replace('-', ' ').replace('_', ' ').split()
            if not words:
                return ''
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

        async def to_pascal_case(s: str) -> str:
            words = s.replace('-', ' ').replace('_', ' ').split()
            return ''.join(word.capitalize() for word in words)

        async def to_snake_case(s: str) -> str:
            s = re.sub(r'[\-\s]+', '_', s)
            s = re.sub(r'([A-Z]+)', r'_\1', s)
            s = s.lower()
            s = re.sub(r'^_+', '', s)
            s = re.sub(r'_+', '_', s)
            return s

        async def to_kebab_case(s: str) -> str:
            s = re.sub(r'[\_\s]+', '-', s)
            s = re.sub(r'([A-Z]+)', r'-\1', s)
            s = s.lower()
            s = re.sub(r'^-+', '', s)
            s = re.sub(r'-+', '-', s)
            return s

        if conversion_type == "upper":
            return message.upper()
        elif conversion_type == "lower":
            return message.lower()
        elif conversion_type == "camelCase":
            return await to_camel_case(message)
        elif conversion_type == "PascalCase":
            return await to_pascal_case(message)
        elif conversion_type == "snake_case":
            return await to_snake_case(message)
        elif conversion_type == "kebab-case":
            return await to_kebab_case(message)
        else:
            logger.error(f'Received an invalid conversion type: {await color(conversion_type)} | Allowed conversion types: {await color(["upper", "lower", "camelCase", "PascalCase", "snake_case", "kebab-case"])}')
            raise ValueError(
                f"Unsupported conversion_type: {conversion_type}")
