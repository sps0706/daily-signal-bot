from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🟢 Signal Bot is Running!"

@app.route("/run")
def run_bot():
    subprocess.run(["python", "multi_stock_signal_bot.py"])
    return "✅ Bot Executed"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
