

alembic upgrade head

uvicorn main:app --reload

python -m app.scripts.setup_generator "Siemens Manufacturing" --factories 2 --machines 3