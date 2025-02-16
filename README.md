# monitors

# Dependencies
1. pipx

# Setup
1. `pipx run virtualenv monitors`
1. `source ./monitors/bin/activate`
1. `pip install -r requirements.txt`

# Run
1. `uvicorn app.main:app --reload`

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