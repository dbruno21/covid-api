# Argentine COVID-19 API

This API uses the [Argentinian Ministry of Health (msal.gob.ar) dataset](http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina)

## Description

This is a fork of [alavarello/covid-api](https://github.com/alavarello/covid-api) that uses Django ORM (QuerySets) for querying the dataset using a database instead of doing it all in memory with pandas. 

The default configured database to be used is PostgreSQL. We use Docker to do all the process of setting the database up and running the http server with a cron already configured to update the database every day.

### Requirements

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/)

## Installation

1. Clone the repository using SSH or HTTP

```shell script
git clone git@github.com:dbruno21/covid-api.git  # with SSH
git clone https://github.com/dbruno21/covid-api.git  # with HTTP
cd covid-api
``` 
2. Copy .env file

```shell script
cp docs/env.txt covid_api/.env  # in development
cp docs/env_production.txt covid_api/.env  # in production
```

**Important**: Once you copy the env file change the secret key for a random string 

## Run (with docker)

3. Run (inside repository root folder)

```shell script
docker-compose up
```

### Manually update data

```shell script
docker exec -it covid-api_web_1 bash
python manage.py update_data  # wait for update to finish
exit
```

**Note**: This may take up to an hour to update.

## Docs
```shell script
# Access swagger
http://localhost:8000/api/v1/swagger/
```
