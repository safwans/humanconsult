import asyncio, ssl, certifi, websockets

uri = "wss://ws-relay-server-711566525822.us-central1.run.app/ws"
ssl_context = ssl.create_default_context(cafile=certifi.where())

async def main():
    async with websockets.connect(uri, ssl=ssl_context) as ws:
        await ws.send("Can I get 25% off?")
        print("✅ Sent. Waiting for reply...")
        while True:
            msg = await ws.recv()
            print("📨 Received:", msg)

asyncio.run(main())
