# High-ROI BTCUSDT Day Trading Strategy

## Overview
This is a highly optimized day trading strategy for BTCUSDT on the 15-minute timeframe, developed by **Boomber**. It is designed to capture daily momentum shifts starting from the **Daily Open**. It leverages **Immediate Entry** execution and filters signals using the **MACD Histogram Slope**.

## Files
- `strategy.py`: Self-contained script for data fetching and backtesting.
- `requirements.txt`: Necessary Python libraries.
- `details.md`: This documentation.

## Risk & Position Sizing
- **Starting Balance**: $1000.00 USD
- **Position Size**: 100% of current equity per trade (to meet the high ROI target).
- **Risk Model**: 1% equity risk per trade (1% Stop Loss on 100% position size).
- **Compounding**: Gains are reinvested into subsequent trades.

## Strategy Rules

### Entry Rules (The "Immediate Slope" Pattern)
*   **Pivot**: Daily Open Price.
*   **Time Window**: Entries are prioritized in the first 12 hours of the trading day.
*   **Execution**: Designed for WebSocket market orders for immediate entry at the pivot price.
*   **Long Entry**:
    1. Previous 15m candle closed **below** the Daily Open.
    2. Current price hits/exceeds the Daily Open.
    3. MACD Histogram is **rising** (Slope > 0) and **positive**.
*   **Short Entry**:
    1. Previous 15m candle closed **above** the Daily Open.
    2. Current price hits/drops below the Daily Open.
    3. MACD Histogram is **falling** (Slope < 0) and **negative**.

### Exit Rules
1.  **Take Profit (TP)**: 3% (Captures significant daily moves).
2.  **Initial Stop Loss (SL)**: 1% (Strict protection).
3.  **Dynamic Trailing Stop (TSL)**:
    *   Set at `3.0 * 15m ATR` from the peak price.
    *   Locks in profit as the trade develops.
4.  **End of Day (EOD)**: Any remaining position is closed at 23:45 UTC.

## Performance (Backtest - 6 Months)
*   **Total ROI**: 72.61%
*   **Average Monthly ROI**: ~12.1%
*   **Win Rate**: 44.67%
*   **Total Longs**: 170
*   **Total Shorts**: 177
*   **Average Daily Wins**: 1.36

## How to Run
1. `pip install -r requirements.txt`
2. `python strategy.py`
