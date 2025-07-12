import yfinance as yf
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from astro_utils import get_astro_flags
from time_cycles import is_time_cycle_day, get_cycle_info

# === Config ===
BOT_TOKEN = "7354257381:AAGZeWQ2ClbrZJ-uw0E1j9UobcOG9su884k"
CHAT_ID = "778441013"
STOCK_LIST_CSV = "nse_bse_stock_list.csv"

def gann_square_of_9(price):
    sqrt_price = np.sqrt(price)
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    return [(sqrt_price + angle / 360) ** 2 for angle in angles]

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    return df.dropna()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    return requests.post(url, data=data)

def generate_signal(symbol, df, astro_boost, time_cycle_hit):
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

        # Enhance Signal Strength
        if signal in ["BUY", "SELL"] and (astro_boost or time_cycle_hit):
            signal = "STRONG " + signal

        return signal, close, rsi, ema
    except:
        return "NEUTRAL", 0, 0, 0

def run_batch_signals():
    stock_list = pd.read_csv(STOCK_LIST_CSV)
    all_signals = []

    astro_flags = get_astro_flags()
    is_astro_today = bool(astro_flags)
    today_str = datetime.now().strftime("%d-%b-%Y")

    for symbol in stock_list['symbol']:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            df = calculate_indicators(df)
            if df.empty:
                continue

            time_hit = is_time_cycle_day(symbol)
            signal, price, rsi, ema = generate_signal(symbol, df, is_astro_today, time_hit)

            all_signals.append({
                "Symbol": symbol,
                "Signal": signal,
                "Price": round(price, 2),
                "RSI": round(rsi, 2),
                "EMA20": round(ema, 2),
                "Astro": "Yes" if is_astro_today else "No",
                "TimeCycle": get_cycle_info(symbol) if time_hit else ""
            })
        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

    df_signals = pd.DataFrame(all_signals)
    df_signals.to_csv("signals_output.csv", index=False)

    actionable = df_signals[df_signals["Signal"] != "NEUTRAL"]
    if not actionable.empty:
        msg = f"📈 *Stock Signals for {today_str}*\n\n"
        for _, row in actionable.iterrows():
            astro = "🌕" if row["Astro"] == "Yes" else ""
            cycle = f"🕒 {row['TimeCycle']}" if row["TimeCycle"] else ""
            msg += f"{row['Symbol']}: *{row['Signal']}* at ₹{row['Price']} {astro} {cycle}\n"
        send_telegram_alert(msg.strip())
        print("✅ Signals sent via Telegram.")
    else:
        send_telegram_alert(f"📊 No actionable signals today.\n{today_str}")
        print("ℹ️ No actionable signals today.")

# === Run the Bot ===
if __name__ == "__main__":
    run_batch_signals()
