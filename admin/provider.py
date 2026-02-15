import bcrypt
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from db.models import Admin


class UsernameAndPasswordProvider(AuthProvider):

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )
        admin: Admin | None = await Admin.check_admin(username=username)
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            request.session.update({"user_id": admin.id, "username": username})
            return response
        raise LoginFailed("Login yoki parol noto'g'ri")

    async def is_authenticated(self, request: Request) -> bool:
        username: str = request.session.get("username", None)
        admin = await Admin.check_admin(username=username)
        if admin:
            username = request.session["username"]
            request.state.user = username
            return True
        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        return AdminConfig(
            app_title="Fast API Admin"
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        print(user, "====================================================")
        return AdminUser(username=user)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
