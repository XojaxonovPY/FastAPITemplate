.PHONY: mig upg down create admin

mig:
	alembic revision --autogenerate -m "Create a baseline migrations"

# Bazani oxirgi versiyagacha yangilash
upg:
	alembic upgrade head

# Bazani boshlang'ich holatga qaytarish
down:
	alembic downgrade base

# Alembic-ni initsializatsiya qilish
create:
	alembic init migrations

run:
	granian --interface asgi main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http 1 --access-log