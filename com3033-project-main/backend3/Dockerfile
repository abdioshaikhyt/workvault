# pull official base image
FROM python:3.13.7

# set work directory
WORKDIR /code/backend3

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
&& apt-get install gcc postgresql postgresql-contrib libpq-dev python3-dev netcat-traditional -y \
&& apt-get clean

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY start.sh /start.sh
COPY start_celery.sh /start_celery.sh
RUN chmod +x /start.sh
RUN chmod +x /start_celery.sh

RUN addgroup --system celery && adduser --system --ingroup celery celery
RUN mkdir -p /celery && chown celery:celery /celery

#Copy the Django project
COPY . .