# BTCUSDT Day Trading Strategy Documentation

## Overview
This is a self-contained day trading strategy for BTCUSDT on the 15-minute timeframe, utilizing the Daily Open price as a key pivot point. It combines MACD Histogram momentum with ATR-based dynamic trailing stops.

## Files
- `strategy.py`: The complete script that fetches data from Binance and runs the backtest.
- `requirements.txt`: List of necessary Python libraries.
- `details.md`: This documentation.

## Indicators Used
1.  **Daily Open Price**: Acts as the daily trend pivot.
2.  **MACD (12, 21, 9)**: The MACD Histogram is used to identify momentum crossovers.
3.  **15m ATR (14)**: Used for dynamic trailing stop-loss to protect profits.

## Strategy Rules

### Entry Rules
*   **Time Filter**: Only look for entries during the first 12 hours of the daily candle (00:00 to 12:00 UTC).
*   **Long Entry**:
    1.  Price is **above** the Daily Open.
    2.  MACD Histogram crosses **above** zero.
*   **Short Entry**:
    1.  Price is **below** the Daily Open.
    2.  MACD Histogram crosses **below** zero.

### Exit Rules
1.  **Take Profit (TP)**: 3% Fixed.
2.  **Stop Loss (SL)**: 1% Fixed Initial.
3.  **Trailing Stop Loss**:
    *   Set at `3.5 * 15m ATR` from price.
    *   Only moves in the direction of the trade once price is in favor.
4.  **End of Day (EOD)**: Any open position is closed at 23:45 UTC.

## Performance (Backtest results - 6 Months)
*   **Compounded ROI**: 14.43%
*   **Sharpe Ratio**: 0.95
*   **Win Rate**: 38.91%
*   **Number of Trades**: 221

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the strategy: `python strategy.py`
