FROM ubuntu:18.04

RUN apt-get update 

RUN apt-get install -y python3-pip && pip3 install --upgrade pip

WORKDIR app


COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_APP=webclient/app.py
ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0

WORKDIR webclient

RUN chmod -R a+rw /app/webclient/data/

RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser
USER appuser

#ENTRYPOINT ["gunicorn", "-b","0.0.0.0:8000", "--access-logfile", "-","app:create_app()"]