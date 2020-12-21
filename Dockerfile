FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY wait-for-postgres.sh /code/
COPY entrypoint.sh /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client && apt-get -y install vim && apt-get install -y cron
RUN ["chmod", "+x", "/code/wait-for-postgres.sh"]
RUN ["chmod", "+x", "/code/entrypoint.sh"]
