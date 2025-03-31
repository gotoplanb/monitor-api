```
##     ##  #######  ##    ## #### ########  #######  ######## 
###   ### ##     ## ###   ##  ##     ##    ##     ## ##     ##
#### #### ##     ## ####  ##  ##     ##    ##     ## ##     ##
## ### ## ##     ## ## ## ##  ##     ##    ##     ## ########  
##     ## ##     ## ##  ####  ##     ##    ##     ## ##   ##  
##     ## ##     ## ##   ###  ##     ##    ##     ## ##    ## 
##     ##  #######  ##    ## ####    ##     #######  ##     ## 
```

"What is the status of ____ ?"

Monitor is a simple service that lets you get and set the status of arbitrary things. Not a system of record but a tool to reduce notification fatigue.

The simplest way to use this is to have some system send an outbound webhook to Monitor to update monitor status then dipslay the status as a PNG badge somewhere.

# Dependencies

1. pipx
1. PostgreSQL database

# Setup

1. `pipx run virtualenv monitor`
1. `source ./monitor/bin/activate`
1. `pip install -r requirements.txt`
1. `pip install -e .`
1. Create a PostgreSQL database at Supabase or similar

or run `make setup`

# Format

1. `black .` or `make format`

# Lint

1. `pylint $(git ls-files '*.py')` or `make lint`

# Test

1. `pytest tests/ -v` or `make test`

# Run

1. Set `DATABASE_URL` through a `.env` file or other environment export
1. `uvicorn app.main:app --reload` or `make run`

# Seed the local database

## Create a monitor

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/monitor/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "test-monitor",
  "tags": ["test"]
}'
```

## Set its state

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/monitor/1/state/' \
  -H 'Content-Type: application/json' \
  -d '{
  "state": "Normal"
}'
```

## Get all statuses

```
curl -X 'GET' \
  'http://localhost:8000/api/v1/monitor/statuses/' \
  -H 'accept: application/json'
```

# Make it public

The easiest way to start is to run this locally and use [Ngrok](https://ngrok.com/docs/getting-started/).

1. Create a Ngrok account at https://ngrok.com/docs/getting-started/
1. Create a domain at https://dashboard.ngrok.com/domains
1. Confirm your local server is running
1. Run `ngrok http --url={{your_domain}} 8000`

The medium-difficult way is to use Heroku or AWS Apprunner.