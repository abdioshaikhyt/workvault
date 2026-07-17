FROM selenium/standalone-chrome:4.35.0

USER root

WORKDIR /code/backend4

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc postgresql postgresql-contrib libpq-dev python3-dev python3-gdbm netcat-traditional \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY start_celery.sh /start_celery.sh
RUN chmod +x /start_celery.sh

RUN addgroup --system celery && adduser --system --ingroup celery celery
RUN mkdir -p /home/celery && chown celery:celery /home/celery
RUN mkdir -p /celery && chown celery:celery /celery
ENV HOME=/home/celery

COPY . .