from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
peers: set[WebSocket] = set()

@app.websocket("/ws")
async def relay(ws: WebSocket):
    await ws.accept()
    peers.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for conn in peers:
                if conn is not ws:
                    try:
                        await conn.send_text(msg)
                    except:
                        peers.discard(conn)
    except WebSocketDisconnect:
        pass
    finally:
        peers.discard(ws)

@app.get("/")
def health():
    return {"status": "ok"}
