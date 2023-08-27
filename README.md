# Portuguese Politics API - Política Para Todos

Extracts information from:

* [public Portuguese Parliament API](https://www.parlamento.pt/Cidadania/Paginas/DadosAbertos.aspx);
* [Política Para Todos community](https://github.com/Politica-Para-Todos).

and expose that information through a simple to use [API](https://portuguese-politics.herokuapp.com/docs).

Currently, the following information is being exposed:
* Portuguese Parliament initiatives;
* Portuguese Parliament vote information;
* Information regarding Portuguese legislative elections.

All information provided is free of use by anyone, so that they can be used for information dissemination or investigation.

# Development 

## Installation

```bash
make setup init
```

## Run the api locally

```bash
make runlocal
```

## Components

1. There is a cronjob in Luís Silva personal computer that extracts the data from Portuguese Parliament to our datalake.
    * Source code executed is `cronjob.py`;
    * This is necessary because requests from Heroku and other cloud providers are rejected;
    * Runs every day at 8 pm Portugal time.
2. The daily updater loads the data from our datalake and extracts the needed information, compute some statistics, and store everything in the datalake to later be consumed by the API.
    * This process takes around 1h (when processing XIV legislature);
    * Source code executed is `src.daily_updater.parliament.main`.
    * Runs every day at 3 am GMT.
3. Heroku dynos sleep after 30 min of inactivity, meaning the daily updater won't run if the dyno is sleeping. Thus we have an Azure Function making requests to our API to avoid that.
    * Source code executed is  `AzureFunctions.PortuguesePoliticsDailyUpdate.src.main.py`
    * Runs every day from 2 am GMT to 5 am GMT at each 20 minutes;
    * We can't let this run the full day becuase Heroku has a limit of 1,000 dyno hours per month for our tier.
4. API runs using Gunicorn and FastAPI
    * Source code executed is `src.app.main`

## Python modules

The Python version used must be one of https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-python, since this is the environment used by Heroku

## Add a new endpoint

1. If a new data source needs to be downloaded from the Portuguese Parliament it is necessary to update the cronjob task
2. Follow the `src.daily_updater` examples to pre-process the data and store it in our datalake
3. Add the new endpoints to `src.app.main`