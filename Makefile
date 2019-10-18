test:
	parallel -j0 --lb ::: 'celery worker --app=app.celery --concurrency=1 --loglevel=INFO' 'flask run'

