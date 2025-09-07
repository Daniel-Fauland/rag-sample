from datetime import timedelta, datetime, timezone
import jwt
import uuid_utils as uid
from config import config
from utils.logging import logger


class JWTHandler():
    @staticmethod
    async def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
        payload = {}
        payload['user'] = user_data
        payload['exp'] = datetime.now(timezone.utc) + (
            expiry if expiry is not None else timedelta(minutes=config.jwt_access_token_expiry))
        payload['jti'] = str(uid.uuid7())
        payload['refresh'] = refresh

        token = jwt.encode(
            payload=payload,
            key=config.jwt_secret,
            algorithm=config.jwt_algorithm
        )
        return token

    @staticmethod
    async def decode_token(token: str) -> dict:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=config.jwt_secret,
                algorithms=[config.jwt_algorithm]
            )
            return token_data
        except jwt.ExpiredSignatureError:
            # Token is expired, return None without logging as an error
            return None
        except jwt.PyJWTError as e:
            logger.warning(f"Could not decode the JWT token: {e}")
            return None


# Example usage and migration helper
if __name__ == "__main__":
    import asyncio

    async def main():
        jwt_handler = JWTHandler()

        # Create a valid access token
        user_data: dict = {
            "id": "123", "email": "admin@example.com", "roles": ["user", "admin"]}
        expiry: timedelta = timedelta(seconds=10)
        refresh: bool = False
        jwt_token = await jwt_handler.create_access_token(user_data, expiry, refresh)
        print(f"JWT_TOKEN (valid): {jwt_token}\n")

        # Create an expired access token
        user_data: dict = {
            "id": "123", "email": "admin@example.com", "roles": ["user", "admin"]}
        expiry: timedelta = timedelta(seconds=0)
        refresh: bool = False
        jwt_token_expired = await jwt_handler.create_access_token(user_data, expiry, refresh)
        print(f"JWT_TOKEN (expired): {jwt_token_expired}\n")

        # Decode valid access token
        payload = await jwt_handler.decode_token(jwt_token)
        print(f"Payload data (valid): {payload}\n")

        # Decode expired access token
        payload = await jwt_handler.decode_token(jwt_token_expired)
        print(f"Payload data (expired): {payload}")

    # Run the async main function
    asyncio.run(main())
