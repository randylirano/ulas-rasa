# Testing Locally

To test the changes locally:

1. `brew services start postgresql@18` --> Start database server
2. `poetry run uvicorn app.main:app --reload` --> Start FastAPI
