from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import asyncio
import random
import logging
from flask import Flask
import threading
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telegram API credentials (same for all accounts)
API_ID = 2587846
API_HASH = "3fa173b2763d7e47971573944bd0971a"

# Load session strings from environment variables
SESSIONS = [
    os.getenv("SESSION_1"),
    os.getenv("SESSION_2"),
    os.getenv("SESSION_3"),
    os.getenv("SESSION_4"),
    os.getenv("SESSION_5"),
    os.getenv("SESSION_6"),
    os.getenv("SESSION_7"),
    os.getenv("SESSION_8"),
]

# Target group ID
GROUP_ID = -1002377798958  # Change as needed

# Flask app for health check
app = Flask(__name__)
PORT = int(os.getenv("PORT", 5000))  # Use environment port if available

@app.route("/")
def health_check():
    return "Bot is running", 200

async def handle_buttons(event, client):
    """Clicks a random inline button when a bot sends a message with buttons."""
    if event.reply_markup and hasattr(event.reply_markup, 'rows'):
        buttons = [btn for row in event.reply_markup.rows for btn in row.buttons if hasattr(btn, "data")]
        if buttons:
            button = random.choice(buttons)
            await asyncio.sleep(random.randint(3, 6))  # Human-like delay
            try:
                await event.click(buttons.index(button))
                logging.info(f"Session ({str(client.session.save())[:10]}...): Clicked button '{button.text}'")
            except Exception as e:
                logging.error(f"Session ({str(client.session.save())[:10]}...): Failed to click button - {e}")

async def process_group(client):
    """Handles the interaction in the Telegram group."""
    @client.on(events.NewMessage(chats=GROUP_ID))
    async def button_click_listener(event):
        if event.sender and event.sender.bot:  # Check if sender is a bot
            await handle_buttons(event, client)

    while True:
        try:
            # Send /explore command
            await client.send_message(GROUP_ID, "/explore")
            logging.info(f"Session ({str(client.session.save())[:10]}...): Sent /explore command")

            # Wait for bot response
            await asyncio.sleep(5)

            # Sleep before sending the next command
            delay = random.randint(305, 310)
            logging.info(f"Session ({str(client.session.save())[:10]}...): Sleeping for {delay} seconds...")
            await asyncio.sleep(delay)

        except Exception as e:
            logging.error(f"Session ({str(client.session.save())[:10]}...): Error - {e}")
            await asyncio.sleep(60)  # Retry after 60 seconds if there's an error

async def start_client(session_string):
    """Starts a Telethon client using a string session."""
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    await client.start()
    logging.info(f"Session ({str(client.session.save())[:10]}...): Client started!")

    await process_group(client)
    await client.run_until_disconnected()

async def run_all_clients():
    tasks = [start_client(session) for session in SESSIONS if session]  # Ensure session exists
    await asyncio.gather(*tasks)

def start_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_clients())

def start_flask():
    app.run(host="0.0.0.0", port=PORT, threaded=True)

if __name__ == "__main__":
    # Start Telethon clients in a separate thread
    telethon_thread = threading.Thread(target=start_telethon, daemon=True)
    telethon_thread.start()

    # Start Flask health check in the main thread
    start_flask()
