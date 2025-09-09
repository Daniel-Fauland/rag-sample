from datetime import timedelta, datetime, timezone
import jwt
import uuid_utils as uid
from config import config
from utils.logging import logger
from database.redis import redis_manager


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

    @staticmethod
    async def add_jwt_to_blacklist(token_data: dict, redis_client=None) -> None:
        """Add a decoded jwt token to a blacklist in redis using its 'jti' identifier"""
        if redis_client is None:
            redis_client = redis_manager.get_client()

        # Calculate TTL from expiration time
        exp_timestamp = token_data['exp']
        current_time = datetime.now(timezone.utc).timestamp()
        ttl_seconds = int(exp_timestamp - current_time)

        await redis_client.setex(f"blacklist:{token_data['jti']}", ttl_seconds, "1")

    @staticmethod
    async def jwt_is_blacklisted(token_data: dict, redis_client=None) -> bool:
        """Check if the given decoded jwt token is currently part of the blacklist in redis"""
        if redis_client is None:
            redis_client = redis_manager.get_client()

        return await redis_client.exists(f"blacklist:{token_data['jti']}")


# Example usage and migration helper
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize Redis connection for testing
        await redis_manager.connect()

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
        payload_expired = await jwt_handler.decode_token(jwt_token_expired)
        print(f"Payload data (expired): {payload_expired}")

        # Get Redis client for testing
        redis_client = redis_manager.get_client()

        # Check if the valid access token is currently part of the redis blacklist
        is_blacklisted = await jwt_handler.jwt_is_blacklisted(payload, redis_client)
        print(
            f"Is the token currently blacklisted (Should be NO): {'YES' if is_blacklisted else 'NO'}")

        # Add the valid access token to the redis blacklist
        await jwt_handler.add_jwt_to_blacklist(payload, redis_client)

        # Check again if the valid access token is currently part of the redis blacklist
        is_blacklisted = await jwt_handler.jwt_is_blacklisted(payload, redis_client)
        print(
            f"Is the token currently blacklisted (Should be YES): {'YES' if is_blacklisted else 'NO'}")

        # Clean up
        await redis_manager.disconnect()

    # Run the async main function
    asyncio.run(main())
