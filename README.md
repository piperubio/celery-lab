example: https://github.com/testdrivenio/fastapi-celery

1. celery -A tasks worker -B --loglevel=INFO
2. uvicorn main:app --reload
3. http://127.0.0.1:8000/docs
