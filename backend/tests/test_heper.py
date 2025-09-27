import uuid
from sqlmodel import select
from database.schemas.users import User
from core.role_assignment.service import RoleAssignmentService
from models.role_assignment.request import RoleAssignmentCreateRequest, RoleAssignmentDeleteRequest

role_assignment_service = RoleAssignmentService()


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

    async def create_role_assignment_if_not_exists(self, db_session, user_id: uuid.UUID, role_id: int):
        assignment_exists: bool = await role_assignment_service.role_assignment_exists(user_id=user_id, role_id=role_id, session=db_session)
        if not assignment_exists:
            role_assignment_data = RoleAssignmentCreateRequest(
                user_id=user_id, role_id=role_id)
            result = await role_assignment_service.create_role_assignment(assignment_data=role_assignment_data, session=db_session)
            assert result

    async def delete_role_assignment_if_exists(self, db_session, user_id: uuid.UUID, role_id: int):
        role_assignment_data = RoleAssignmentDeleteRequest(
            user_id=user_id, role_id=role_id)
        _ = await role_assignment_service.delete_role_assignment(assignment_data=role_assignment_data, session=db_session)

    async def create_admin_user_if_not_exists(self, client, db_session, payload=None):
        user = await self.create_user_if_not_exists(client, db_session, payload)
        await self.create_role_assignment_if_not_exists(
            db_session=db_session, user_id=user.id, role_id=1)
        return user

    async def create_user_no_permissions(self, client, db_session, payload=None):
        user = await self.create_user_if_not_exists(client, db_session, payload)
        await self.delete_role_assignment_if_exists(
            db_session=db_session, user_id=user.id, role_id=2)
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

    async def login_user_with_type(self, client, db_session, user_type="normal", email_suffix=""):
        """Helper to create and login different types of users"""
        email = f"test_{user_type}_{email_suffix}@example.com"

        if user_type == "admin":
            user = await self.create_admin_user_if_not_exists(client, db_session, payload={"email": email})
        elif user_type == "no_permissions":
            user = await self.create_user_no_permissions(client, db_session, payload={"email": email})
        else:  # normal user
            user = await self.create_user_if_not_exists(client, db_session, payload={"email": email})

        # Login the user
        login_payload = {
            "email": user.email,
            "password": "Strongpassword123-"
        }
        response = await client.post("/user/login", json=login_payload)
        data = response.json()
        assert response.status_code == 201
        return data, user
