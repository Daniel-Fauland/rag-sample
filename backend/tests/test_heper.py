import uuid
from sqlmodel import select
from database.schemas.users import User


class TestHelper():
    async def create_user_if_not_exists(self, client, db_session, payload=None):
        """Create a user if not exist in the db

        Args:
            client: Test client for making HTTP requests
            db_session: Database session for querying
            payload: Optional dict with user data. Missing fields will use defaults.
                    Fields: first_name, last_name, email, password
        """
        # Generate unique email for each test run
        unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

        # Define the default request payload
        default_payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": unique_email,
            "password": "Strongpassword123-"
        }

        # Merge provided payload with defaults
        if payload is None:
            payload = default_payload
        else:
            # Start with defaults and update with provided values
            final_payload = default_payload.copy()
            final_payload.update(payload)
            payload = final_payload

        statement = select(User).where(User.email == payload["email"])
        result = await db_session.exec(statement)
        user = result.first()
        if user is None:
            # Perform POST request
            response = await client.post("/user/signup", json=payload)
            # Assertions
            assert response.status_code == 201
            statement = select(User).where(User.email == payload["email"])
            result = await db_session.exec(statement)
            user = result.first()
        return user

    async def login_user(self, client, db_session, payload=None):
        user = await self.create_user_if_not_exists(client, db_session, payload)

        login_payload = {
            "email": user.email,
            "password": "Strongpassword123-"
        }
        response = await client.post("/user/login", json=login_payload)
        data = response.json()
        assert response.status_code == 201
        return data
