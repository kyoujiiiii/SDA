cd AirLock-back/


cp .env.example .env


python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
