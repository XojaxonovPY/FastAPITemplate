from invoke import task


@task
def mig(c):
    c.run('alembic revision --autogenerate -m "Create a baseline migrations"')


@task
def upg(c):
    c.run("alembic upgrade head")


@task
def down(c):
    c.run("alembic downgrade head")


@task
def create(c):
    c.run("alembic init migrations")


@task
def admin(c):
    c.run('uvicorn admin.app:app --host localhost --port 8005')
