# XAUUSD Telegram AI Bot

## Features
- Multi-timeframe analysis (H4 → M15)
- Trend, momentum, volatility, liquidity sweep, fair value gap
- London & NY session filter
- High-confluence scoring
- Telegram alerts with entry / SL / TP

## Setup
1. Create a Telegram Bot (@BotFather)
2. Get your Chat ID (@userinfobot)
3. Replace BOT_TOKEN and CHAT_ID in bot.py
4. Push this repo to GitHub
5. Deploy to Render / Railway:
   - Build command: pip install -r requirements.txt
   - Start command: python bot.py
6. Receive Telegram alerts
