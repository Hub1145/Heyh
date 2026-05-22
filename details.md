# High-ROI BTC Day Trading Bot (Robinhood)

## Overview
This project provides an automated day trading bot for BTC on Robinhood, utilizing an optimized **Daily Open + MACD Slope** strategy.

## Files
- `strategy.py`: Historical backtesting script.
- `bot.py`: Live trading bot script.
- `requirements.txt`: Python dependencies.
- `.env.example`: Credentials template.

## Strategy Summary
- **Pivot**: Daily Open price.
- **Indicators**: MACD (12, 21, 9) slope and ATR (14).
- **Logic**: Enter Long when price is above Daily Open and MACD Histogram is rising.
- **Risk**: 10% Position Size ($1000 start), 1% Stop Loss, 3% Take Profit, 3.0x ATR Trailing Stop.

## Performance (6 Months)
- **Total ROI**: 72.61%
- **Win Rate**: 44.67%
- **Avg Daily Wins**: 1.36

## Live Bot Setup
1. **Credentials**: Copy `.env.example` to `.env` and enter your Robinhood email and password.
2. **Installation**: `pip install -r requirements.txt`
3. **Run**: `python bot.py`
    - By default, the bot runs in **Dry Run** mode.
    - Set `dry_run=False` in `bot.py` to enable live execution.

## Safety Note
This bot uses market orders for immediate execution as requested. Trading carries significant risk. Start with a small position size or use the default `dry_run=True` to verify behavior.
