import os
from flask import Flask
import threading
import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def start_bot():
    import asyncio
    asyncio.run(bot.main())

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
