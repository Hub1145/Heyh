# Improved BTCUSDT Day Trading Strategy Documentation

## Overview
This is an optimized self-contained day trading strategy for BTCUSDT on the 15-minute timeframe. It leverages the Daily Open price as a key pivot point and uses MACD Histogram (12, 21, 9) for entry timing and 15m ATR for dynamic trailing stop management.

## Files
- `strategy.py`: The complete script (data fetching + backtesting).
- `requirements.txt`: Python library dependencies.
- `details.md`: This documentation.

## Strategy Rules

### Entry Rules
*   **Time Window**: Entries are only allowed in the first 12 hours of the daily candle (00:00 to 12:00 UTC).
*   **Long Entry**:
    1.  Price is **above** the Daily Open.
    2.  MACD Histogram crosses **above** zero (Current > 0, Previous <= 0).
*   **Short Entry**:
    1.  Price is **below** the Daily Open.
    2.  MACD Histogram crosses **below** zero (Current < 0, Previous >= 0).

### Exit Rules
1.  **Take Profit (TP)**: 3% Fixed.
2.  **Initial Stop Loss (SL)**: 1% Fixed.
3.  **Dynamic Trailing Stop (TSL)**:
    *   Set at `4.5 * 15m ATR` from the current price.
    *   Only trails in the profitable direction.
    *   **Priority**: TP > TSL > SL.
4.  **End of Day (EOD)**: Any open position is closed at 23:45 UTC.

## Performance (Optimized - 6 Months)
*   **Compounded ROI**: 31.47%
*   **Sharpe Ratio**: 1.74
*   **Win Rate**: 40.58%
*   **Total Trades**: 207

## Key Improvements
*   **Exit Prioritization**: TP is checked before trailing stops to capture fast momentum peaks.
*   **TSL Optimization**: Increased trailing multiplier to 4.5*ATR to give the trade more room to breathe while still protecting against sharp reversals.
*   **Compounding**: Performance now accounts for compounded returns.

## How to Run
1. `pip install -r requirements.txt`
2. `python strategy.py`
