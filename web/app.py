from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from db import engine
from db.models import User
from web.provider import UsernameAndPasswordProvider

app = Starlette()
admin = Admin(engine,
              title='P_29Admin',
              base_url='/',
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="sdgfhjhhsfdghn")]
              )
admin.add_view(ModelView(User))
admin.mount_to(app)


import bcrypt

print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))

