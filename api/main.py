# main.py
import os, uuid, json, time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK



# Config
WS_URL = os.getenv("RELAY_WS", "wss://ws-relay-server-711566525822.us-central1.run.app/ws")
TIMEOUT_SEC = int(os.getenv("WAIT_SEC", "60"))
CONNECT_TMO = float(os.getenv("WS_CONNECT_TMO", 3.0))  # seconds

app = FastAPI()


# Define expected input using Pydantic
class MessagePayload(BaseModel):
    message: str


@app.get("/")
def health_check():
    return {"status": "Running", "id": 123}


@app.post("/api")
def request_approval(data: MessagePayload):
    req_id = str(uuid.uuid4())
    payload = {"id": req_id, "message": data.message}

    start = time.time()
    try:
        with connect(WS_URL, open_timeout=CONNECT_TMO) as ws:
            ws.send(json.dumps(payload))
            while time.time() - start < TIMEOUT_SEC:
                try:
                    resp = json.loads(ws.recv())
                    if resp.get("id") == req_id and "decision" in resp:
                        return {"id": req_id, "decision": resp["decision"]}
                except ConnectionClosedOK:
                    break  # Clean close from server
    except Exception as exc:
        raise HTTPException(502, f"WebSocket relay failed: {exc}")

    return {"id": req_id, "status": "pending"}  # No decision within timeout
