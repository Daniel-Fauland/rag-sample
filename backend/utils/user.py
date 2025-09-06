from argon2_hasher import Argon2Hasher
from utils.logging import logger


class UserHelper():
    @staticmethod
    async def hash_password(password: str) -> str:
        """
        Hash a password using Argon2id with secure defaults based on OWASP 2024 recommendations.

        Args:
            password (str): The plain text password to hash

        Returns:
            str: The hashed password as a string

        Raises:
            ValueError: If password is empty
            TypeError: If password is not a string
            Exception: If hashing fails
        """
        # Input validation
        if not isinstance(password, str):
            logger.error(f"Password must be a string not '{type(password)}'")
            raise TypeError("Password must be a string")

        if not password:
            logger.error("Password cannot be empty")
            raise ValueError("Password cannot be empty")

        try:
            return Argon2Hasher.hash(password)
        except Exception as e:
            logger.error(f"Failed to hash password: {str(e)}")
            raise Exception(f"Failed to hash password: {str(e)}")

    @staticmethod
    async def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its Argon2 hash.

        Args:
            password (str): The plain text password to verify
            hashed_password (str): The stored hash to check against

        Returns:
            bool: True if password matches, False otherwise
        """
        if not isinstance(password, str) or not isinstance(hashed_password, str):
            logger.warning(
                f"Returning false due to invalid data types. password: {type(password)} | hashed_password: {type(hashed_password)}")
            return False

        try:
            return Argon2Hasher.verify(hashed_password, password)
        except Exception as e:
            # Any other exception should be treated as verification failure
            logger.error(f"Failed to verify password hash: {str(e)}")
            return False


# Example usage and migration helper
if __name__ == "__main__":
    import asyncio

    async def main():
        user_helper = UserHelper()
        # Hash a password with 2024 security standards
        plain_password = "Userpassword"

        print("=== Argon2id Password Hashing Example ===")

        # Hash password
        hashed = await user_helper.hash_password(plain_password)
        print(f"Original password: {plain_password}")
        print(f"Argon2id hash: {hashed}")

        # Verify correct password
        is_valid = await user_helper.verify_password(plain_password, hashed)
        print(f"Password verification (correct): {is_valid}")

        # Verify wrong password
        is_invalid = await user_helper.verify_password("WrongPassword", hashed)
        print(f"Password verification (wrong): {is_invalid}")

        # Verify wrong data type
        is_invalid = await user_helper.verify_password([plain_password], hashed)
        print(f"Password verification (invalid): {is_invalid}")

    # Run the async main function
    asyncio.run(main())
