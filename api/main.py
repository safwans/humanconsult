import os, uuid, json, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK

# Config
WS_URL = os.getenv("RELAY_WS", "wss://ws-relay-server-711566525822.us-central1.run.app/ws")
TIMEOUT_SEC = int(os.getenv("WAIT_SEC", "60"))
CONNECT_TMO = float(os.getenv("WS_CONNECT_TMO", 3.0))  # seconds

app = FastAPI()

class MessagePayload(BaseModel):
    message: str

@app.get("/")
def health_check():
    return {"status": "Running", "id": 123}

@app.post("/api")
def request_approval(data: MessagePayload):
    payload = {"id": str(uuid.uuid4()), "message": data.message}

    try:
        with connect(WS_URL, open_timeout=CONNECT_TMO) as ws:
            ws.send(json.dumps(payload))
            start = time.time()

            while time.time() - start < TIMEOUT_SEC:
                try:
                    raw = ws.recv()
                    if not raw:
                        continue

                    # Try to parse as JSON
                    try:
                        resp = json.loads(raw)
                        return {"reply": resp}
                    except json.JSONDecodeError:
                        return {"reply": raw.strip()}

                except ConnectionClosedOK:
                    break  # server closed connection

    except Exception as exc:
        raise HTTPException(502, f"WebSocket relay failed: {exc}")

    return {"status": "pending"}
