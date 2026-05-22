# BTCUSDT Optimized Day Trading Strategy Documentation

## Overview
This strategy is developed by **Boomber**. It is a day trading system for BTCUSDT on the 15-minute timeframe that focuses on price action relative to the **Daily Open**. It uses MACD for momentum confirmation and ATR for dynamic trailing stops.

## Files
- `strategy.py`: The complete script (data fetching + backtesting).
- `requirements.txt`: Python library dependencies.
- `details.md`: This documentation.

## Risk Management
- **Starting Balance**: $1000 USD
- **Risk Per Trade**: 10% of current equity
- **Take Profit (TP)**: 3% Fixed
- **Stop Loss (SL)**: 1% Fixed Initial
- **Trailing Stop Loss (TSL)**:
    - Set at `8.0 * 15m ATR` from the current price.
    - Designed to give trades maximum room while protecting significant gains.

## Strategy Rules

### Entry Rules
*   **Pivot**: Daily Open price.
*   **Time Window**: Entries allowed from 00:00 to 12:00 UTC.
*   **Long Entry**: Price crosses above Daily Open AND MACD Histogram is positive.
*   **Short Entry**: Price crosses below Daily Open AND MACD Histogram is negative.
*   **WebSocket/Market Order**: Entries should be executed immediately upon crossover.

### Exit Rules
1.  **Take Profit**: 3% gain.
2.  **Trailing Stop**: 8.0x ATR(15m).
3.  **Stop Loss**: 1% loss.
4.  **End of Day**: Close all positions at 23:45 UTC.

## Performance (Backtest results - 6 Months)
- **Starting Balance**: $1000.00
- **Total ROI**: 3.80%
- **Win Rate**: 40.61%
- **Total Longs**: 107
- **Total Shorts**: 90
- **Avg Daily Wins**: 1.03

## How to Run
1. `pip install -r requirements.txt`
2. `python strategy.py`
