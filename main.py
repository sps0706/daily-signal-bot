from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "🟢 Signal Bot is Running!"

@app.route("/run")
def run_bot():
    subprocess.run(["python", "multi_stock_signal_bot.py"])
    return "✅ Bot Executed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
