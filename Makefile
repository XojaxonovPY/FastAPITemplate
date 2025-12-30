PORT = 8005
HOST = localhost

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

# Admin panelni ishga tushirish
admin:
	uvicorn admin.app:app --host $(HOST) --port $(PORT)
