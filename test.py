from telethon import TelegramClient, events, Button
import asyncio
import random
import logging
from flask import Flask
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telegram API credentials
ACCOUNTS = [
    {"session": "session1", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
    {"session": "session2", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"},
    {"session": "session3", "api_id": 2587846, "api_hash": "3fa173b2763d7e47971573944bd0971a"}
]

GROUP_ID = -1002377798958  # Provided group ID

# Flask app for health check
app = Flask(__name__)

@app.route("/")
def health_check():
    return "Bot is running", 200

async def handle_buttons(event):
    """Clicks a random inline button when a bot sends a message with buttons."""
    if event.reply_markup and hasattr(event.reply_markup, 'rows'):
        buttons = [btn for row in event.reply_markup.rows for btn in row.buttons if hasattr(btn, "data")]
        if buttons:
            button = random.choice(buttons)
            await asyncio.sleep(random.randint(3, 6))  # Human-like delay
            try:
                await event.click(buttons.index(button))
                logging.info(f"Clicked button: {button.text} in response to {event.sender_id}")
            except Exception as e:
                logging.error(f"Failed to click button: {e}")

async def process_group(client):
    """Handles the interaction in the Telegram group."""
    @client.on(events.NewMessage(chats=GROUP_ID))
    async def button_click_listener(event):
        if event.sender and event.sender.bot:  # Check if sender is a bot
            await handle_buttons(event)

    while True:
        try:
            # Send /explore command
            await client.send_message(GROUP_ID, "/explore")
            logging.info(f"{client.session.filename}: Sent /explore command")

            # Wait for bot response
            await asyncio.sleep(5)

            # Sleep before sending the next command
            delay = random.randint(305, 310)
            logging.info(f"{client.session.filename}: Sleeping for {delay} seconds...")
            await asyncio.sleep(delay)

        except Exception as e:
            logging.error(f"{client.session.filename}: Error: {e}")
            await asyncio.sleep(60)  # Retry after 60 seconds if there's an error

async def start_client(account):
    """Starts a Telethon client and listens for button messages."""
    client = TelegramClient(account["session"], account["api_id"], account["api_hash"])
    await client.start()
    logging.info(f"{account['session']} started!")

    await process_group(client)
    await client.run_until_disconnected()

async def run_all_clients():
    tasks = [start_client(account) for account in ACCOUNTS]
    await asyncio.gather(*tasks)

def start_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_clients())

def start_flask():
    app.run(host="0.0.0.0", port=5000, threaded=True)

if __name__ == "__main__":
    # Start Telethon clients in a separate thread
    telethon_thread = threading.Thread(target=start_telethon, daemon=True)
    telethon_thread.start()

    # Start Flask health check in the main thread
    start_flask()
