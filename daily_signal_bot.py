import yfinance as yf
import numpy as np
import pandas as pd
import requests
from datetime import datetime

# === Configuration ===
BOT_TOKEN = "7354257381:AAGZeWQ2ClbrZJ-uw0E1j9UobcOG9su884k"
CHAT_ID = "778441013"
STOCK_SYMBOL = "ASIANPAINT.NS"

# === Gann Square of 9 Calculation ===
def gann_square_of_9(price):
    sqrt_price = np.sqrt(price)
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    return [(sqrt_price + angle / 360) ** 2 for angle in angles]

# === RSI Indicator ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# === Add Technical Indicators ===
def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    return df

# === Telegram Bot Alert ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Alert sent successfully!")
    else:
        print("❌ Failed to send alert:", response.text)

# === Generate Buy/Sell/Neutral Signal ===
def generate_signal(df):
    df = df.dropna()
    if df.empty:
        return "NEUTRAL", 0, 0, 0

    latest = df.iloc[-1]
    gann_levels = gann_square_of_9(latest['Close'])

    try:
        rsi = float(latest['RSI'])
        close = float(latest['Close'])
        ema = float(latest['EMA20'])

        if rsi > 60 and close > ema and close > max(gann_levels[:4]):
            signal = "BUY"
        elif rsi < 40 and close < ema and close < min(gann_levels[4:]):
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        return signal, close, rsi, round(ema, 2)
    except:
        return "NEUTRAL", 0, 0, 0

# === Main Execution ===
def run():
    df = yf.download(STOCK_SYMBOL, period="3mo", interval="1d")
    df = calculate_indicators(df)
    signal, price, rsi, ema20 = generate_signal(df)

    date_str = datetime.now().strftime("%d-%b-%Y")
    message = f"📈 *Signal for {STOCK_SYMBOL} on {date_str}*\n\n" \
              f"Price: ₹{price:.2f}\nRSI: {rsi:.2f}\nEMA20: ₹{ema20}\n" \
              f"📊 Gann + RSI + EMA Filter\n\n" \
              f"🟢 *Signal*: {signal}"

    send_telegram_alert(message)
    print("Sent message:\n", message)

# Run the bot
if __name__ == "__main__":
    run()
