from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from admin.provider import UsernameAndPasswordProvider
from db import engine
from db.models import User

app = Starlette()
admin = Admin(engine,
              title='Fast API Admin',
              base_url='/',
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="sdgfhjhhsfdghn")]
              )
admin.add_view(ModelView(User))
admin.mount_to(app)
