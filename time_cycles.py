import datetime

# === Manually Defined Swing Dates (Add more as needed) ===
swing_dates = {
    "ASIANPAINT.NS": "2024-10-25",
    "TCS.NS": "2024-11-05",
    "RELIANCE.NS": "2024-10-30",
    "HDFCBANK.NS": "2024-10-18",
    "INFY.NS": "2024-11-02"
}

# Fibonacci day cycles
fibo_days = [21, 34, 55, 89, 144]

def is_time_cycle_day(symbol, today=None):
    if today is None:
        today = datetime.date.today()
    if symbol not in swing_dates:
        return False
    start_date = datetime.datetime.strptime(swing_dates[symbol], "%Y-%m-%d").date()
    days_elapsed = (today - start_date).days
    return days_elapsed in fibo_days

def get_cycle_info(symbol, today=None):
    if today is None:
        today = datetime.date.today()
    if symbol not in swing_dates:
        return None
    start_date = datetime.datetime.strptime(swing_dates[symbol], "%Y-%m-%d").date()
    days_elapsed = (today - start_date).days
    if days_elapsed in fibo_days:
        return f"{days_elapsed}-day cycle"
    return None
