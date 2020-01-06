FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3-pip && pip3 install --upgrade pip

WORKDIR app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_APP=/app/webclient/app.py
ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000  --access-logfile -"

WORKDIR webclient
COPY webclient .

CMD ["gunicorn","app:app"]
