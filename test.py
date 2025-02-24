from telethon import TelegramClient, events, Button
import asyncio
import random
import os
from flask import Flask

# Telegram API credentials (using the same API ID and API hash for all accounts)
ACCOUNTS = [
    {"session": "session1", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
    {"session": "session2", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
    {"session": "session3", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
    {"session": "session4", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
]

GROUP_ID = -1002377798958  # Provided group ID

# Flask app for health check
app = Flask(__name__)

@app.route("/")
def health_check():
    return "Bot is running", 200

async def process_group(client):
    while True:
        try:
            # Send /explore command
            await client.send_message(GROUP_ID, "/explore")
            print(f"{client.session.filename}: Sent /explore command")

            # Wait for response
            await asyncio.sleep(5)

            async for message in client.iter_messages(GROUP_ID, limit=10):
                if message.buttons:
                    for row in message.buttons:
                        for button in row:
                            if isinstance(button, Button):
                                await message.click(button.index)
                                print(f"{client.session.filename}: Clicked button: {button.text}")
                                await asyncio.sleep(random.uniform(2, 5))  # Human-like delay

            # Wait before repeating
            delay = random.randint(305, 310)
            print(f"{client.session.filename}: Sleeping for {delay} seconds...")
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"{client.session.filename}: Error: {e}")
            await asyncio.sleep(60)  # Retry after 60 seconds on error

async def start_client(account):
    client = TelegramClient(account["session"], account["api_id"], account["api_hash"])
    await client.start()
    print(f"{account['session']} started!")
    await process_group(client)

async def main():
    tasks = [start_client(account) for account in ACCOUNTS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import threading

    # Start Telethon clients in a separate thread
    threading.Thread(target=lambda: asyncio.run(main()), daemon=True).start()

    # Run Flask app for TCP health check
    app.run(host="0.0.0.0", port=5000)
