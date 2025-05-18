# Gene Report FastAPI Streaming API

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the FastAPI server

```bash
venv/bin/uvicorn api:app  --reload

or

venv/bin/uvicorn api:app 
```

## Usage

POST to `/stream-report` with JSON body:

```json
{
  "file_content": "<file_content>",
  "user_profile": "",
  "file_type": "text_23andme"
}
```

Example using `curl` (with SSE client):

```bash
curl -N -X POST -H "Content-Type: application/json" 
  -d '{  "file_content": "<file_content>",
  "user_profile": "<add a user profile in text>",
  "file_type": "text_23andme"}' 
  http://localhost:8000/stream-report
```

The response will be streamed as Server-Sent Events (SSE) with agent updates. 