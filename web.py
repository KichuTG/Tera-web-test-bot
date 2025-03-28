import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run():
    port = int(os.getenv("PORT", 8080))  # Use Koyeb's assigned port
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)  # Ensure the thread exits when the bot stops
    t.start()
