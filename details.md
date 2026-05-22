# High-ROI BTC Robinhood Trading Bot

## Overview
Automated day trading bot for BTC on the Robinhood platform. It uses the **Immediate Slope** pattern based on the Daily Open pivot, optimized for high returns.

## Core Strategy (Parameters for 72.61% ROI)
- **Timeframe**: 15-minute.
- **Pivot**: Daily Open Price.
- **Indicators**: MACD (12, 26, 9) slope and ATR (14).
- **Position Size**: 100% of current equity per trade (to meet high ROI target).
- **Take Profit (TP)**: 3.0%
- **Initial Stop Loss (SL)**: 1.0%
- **Trailing Stop (TSL)**: 3.0x ATR(15m).
- **Time Window**: Entry allowed 00:00 - 12:00 UTC.

## Files
- `strategy.py`: Backtesting and data acquisition script.
- `bot.py`: Live trading script for Robinhood.
- `requirements.txt`: Python library dependencies.
- `details.md`: This documentation.

## Performance Summary (Backtest - 6 Months)
- **ROI**: 72.61%
- **Win Rate**: 44.67%
- **Number of Longs**: 170
- **Number of Shorts**: 177
- **Avg Daily Wins**: 1.36

## Live Bot Configuration
The configuration is **hardcoded** in `bot.py` for immediate deployment as requested:
1. Open `bot.py`.
2. Update `ROBINHOOD_USER` and `ROBINHOOD_PASS`.
3. Set `DRY_RUN = False` to enable live market orders.
4. Run: `python bot.py`

## Risk Disclaimer
This bot uses market orders and executes trades using 100% of equity as requested. High returns come with high risk. Ensure you understand the logic before running in live mode.
