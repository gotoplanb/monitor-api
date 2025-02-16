```
##     ##  #######  ##    ## #### ########  #######  ########   ######  
###   ### ##     ## ###   ##  ##     ##    ##     ## ##     ## ##    ## 
#### #### ##     ## ####  ##  ##     ##    ##     ## ##     ## ##       
## ### ## ##     ## ## ## ##  ##     ##    ##     ## ########   ######  
##     ## ##     ## ##  ####  ##     ##    ##     ## ##   ##         ## 
##     ## ##     ## ##   ###  ##     ##    ##     ## ##    ##  ##    ## 
##     ##  #######  ##    ## ####    ##     #######  ##     ##  ######  
```

"What is the status of ____ ?"

Monitors is a simple service that lets you get and set the status of arbitrary things. Not a system of record but a tool to reduce notification fatigue.

The simplest way to use this is to have some system send an outbound webhook to Monitors to update monitor status then dipslay the status as a PNG badge somewhere.

# Dependencies

1. pipx

# Setup

1. `pipx run virtualenv monitors`
1. `source ./monitors/bin/activate`
1. `pip install -r requirements.txt`

# Running

1. `uvicorn app.main:app --reload`

# Testing

1. `black .`
1. `pylint $(git ls-files '*.py')`
1. TODO Unit tests

# Seed the local database

## Create a monitor

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/monitors/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "test-monitor",
  "tags": ["test"]
}'
```

## Set its state

```
curl -X 'POST' \
  'http://localhost:8000/api/v1/monitors/1/state/' \
  -H 'Content-Type: application/json' \
  -d '{
  "state": "Normal"
}'
```

## Get all statuses

```
curl -X 'GET' \
  'http://localhost:8000/api/v1/monitors/statuses/' \
  -H 'accept: application/json'
```

# Make it public

The easiest way to start is to run this locally and use [Ngrok](https://ngrok.com/docs/getting-started/).

1. Create a Ngrok account at https://ngrok.com/docs/getting-started/
1. Create a domain at https://dashboard.ngrok.com/domains
1. Confirm your local server is running
1. Run `ngrok http --url={{your_domain}} 8000`