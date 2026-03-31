web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:$PORT
worker: celery -A backend.celery_app worker --loglevel=info
beat: celery -A backend.celery_app beat --loglevel=info
