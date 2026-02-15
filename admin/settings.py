import asyncio

import bcrypt

from db.models import Admin


async def add_user():
    admin_data = {
        "username": input("Username:"),
        "password": bcrypt.hashpw(input("Password:").encode(), salt=bcrypt.gensalt()).decode()
    }
    await Admin.create_admin(**admin_data)


if __name__ == '__main__':
    asyncio.run(add_user())
