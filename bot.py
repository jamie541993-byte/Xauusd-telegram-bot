import requests
import numpy as np
import pandas as pd
import time
from datetime import datetime

# =========================
# TELEGRAM CONFIG
# =========================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "PASTE_YOUR_CHAT_ID_HERE"

# =========================
# MOCK DATA (replace with real feed later)
# =========================
def load_data(timeframe="M15"):
    prices = np.cumsum(np.random.randn(800)) + 1900
    return pd.DataFrame({"close": prices})

# =========================
# SESSION FILTER
# =========================
def london_ny_session():
    hour = datetime.utcnow().hour
    return (7 <= hour <= 11) or (13 <= hour <= 16)

# =========================
# NEWS BLACKOUT FILTER
# =========================
def news_safe():
    return True

# =========================
# MARKET STRUCTURE MULTI-TF
# =========================
def market_structure(df):
    hh = df.close.iloc[-1] > df.close.iloc[-20]
    hl = df.close.iloc[-10] > df.close.iloc[-30]
    lh = df.close.iloc[-1] < df.close.iloc[-20]
    ll = df.close.iloc[-10] < df.close.iloc[-30]
    if hh and hl: return 1
    if lh and ll: return -1
    return 0

# =========================
# TREND FILTER
# =========================
def trend(df):
    ema50 = df.close.ewm(span=50).mean()
    ema200 = df.close.ewm(span=200).mean()
    return 1 if ema50.iloc[-1] > ema200.iloc[-1] else -1

# =========================
# MOMENTUM
# =========================
def momentum(df):
    delta = df.close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    if rsi.iloc[-1] > 55: return 1
    if rsi.iloc[-1] < 45: return -1
    return 0

# =========================
# VOLATILITY FILTER
# =========================
def volatility(df):
    atr = df.close.diff().abs().rolling(14).mean()
    return atr.iloc[-1] > atr.mean()

# =========================
# LIQUIDITY SWEEP
# =========================
def liquidity_sweep(df):
    recent_high = df.close.iloc[-40:-1].max()
    recent_low = df.close.iloc[-40:-1].min()
    if df.close.iloc[-1] > recent_high: return -1
    if df.close.iloc[-1] < recent_low: return 1
    return 0

# =========================
# FAIR VALUE GAP
# =========================
def fair_value_gap(df):
    gap = abs(df.close.iloc[-1] - df.close.iloc[-5])
    avg = df.close.diff().abs().mean()
    return gap > avg * 1.5

# =========================
# AI CONFLUENCE ENGINE
# =========================
def analyze():
    if not london_ny_session(): return None
    if not news_safe(): return None
    dfs = {"H4": load_data("H4"), "H1": load_data("H1"), "M15": load_data("M15")}
    scores = []
    for tf, df in dfs.items():
        structure = market_structure(df)
        tr = trend(df)
        mom = momentum(df)
        vol = volatility(df)
        sweep = liquidity_sweep(df)
        fvg = fair_value_gap(df)
        score = 0
        score += 20 if structure != 0 else 0
        score += 20 if structure == tr else 0
        score += 15 if mom == tr else 0
        score += 15 if vol else 0
        score += 15 if sweep == tr else 0
        score += 15 if fvg else 0
        scores.append((tf, structure, tr, mom, vol, sweep, fvg, score))
    avg_score = np.mean([s[7] for s in scores])
    if avg_score < 85: return None
    votes = [s[2] for s in scores]
    bias_val = 1 if votes.count(1) > votes.count(-1) else -1
    bias = "BULLISH 🟢" if bias_val == 1 else "BEARISH 🔴"
    entry = dfs["M15"].close.iloc[-1]
    sl = entry - 20 if bias_val == 1 else entry + 20
    tp = entry + 40 if bias_val == 1 else entry - 40
    return bias, avg_score, scores, entry, sl, tp

# =========================
# TELEGRAM ALERT
# =========================
def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# MAIN LOOP
# =========================
while True:
    result = analyze()
    if result:
        bias, avg_score, scores, entry, sl, tp = result
        msg = f"🔔 XAUUSD HIGH-CONFLUENCE ALERT\n\nBias: {bias}\nConfidence: {round(avg_score)}%\n\nTimeframes:\n"
        for s in scores:
            tf, structure, tr, mom, vol, sweep, fvg, score = s
            msg += f"{tf}: Score {score}, Trend {'Bullish' if tr==1 else 'Bearish'}, Mom {'Strong' if mom!=0 else 'Weak'}\n"
        msg += f"\nEntry: {entry}\nSL: {sl}\nTP: {tp}\n\n⚠️ Wait for candle confirmation\n📌 Educational use only"
        send_alert(msg)
    time.sleep(900)  # 15 minutes
