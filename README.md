
# Tasks API

FastAPI RESTful API for the Sabermine backend test

# Setup

## Environment

First, create a new virtual envionment in the root directory (sabermine-test/) with 

```
python -m venv .venv 
``` 
and activate it using 
```
source .venv/bin/activate
```

Once complete install all dependencies using 

```
pip install -r requirements.txt
```

## Database Setup 
Since we're using a local database for the time being, set this database up by running 
```
alembic upgrade head
```
which applies migrations and creates the relevant tables


## (Option 1) Run using uvicorn 
To test this locally without docker, simply run 
```
uvicorn app.main:app --reload
```

## (Option 2) Run using docker 
To run this using docker, we must first build the docker image with 

```
docker build -t task-api .
```

and then create the corresponding container using 

```
docker run -p 8000:8000 --name task-api task-api
```


# Running tests 

Once setup is complete, you can run tests simply by running 
```
pytest
```
in root 

# Notes 

The repo is configured to run black to ensure PEP8 styling, and pytest to ensure the tests pass, failure to verify each of these will cause the pipeline to fail


