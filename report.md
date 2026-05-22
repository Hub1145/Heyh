# BTCUSDT Strategy Backtest Performance Report

This report provides a detailed performance analysis of the **Immediate Slope** day trading strategy for BTCUSDT, conducted over a 6-month historical period.

## Executive Summary
- **Period:** November 2025 – May 2026 (180 Days)
- **Timeframe:** 15-Minute
- **Starting Balance:** $1000.00
- **Ending Balance:** $1726.17
- **Total Net Profit:** $726.17
- **Total ROI:** **72.62%**
- **Overall Win Rate:** 44.67%
- **Profit Factor:** 1.54
- **Overall Sharpe Ratio:** 2.66
- **Max Drawdown:** 7.78%

## Strategy Parameters & Risk Model
The backtest was executed using a compounded growth model with strict risk controls:
- **Starting Capital:** $1000.00
- **Position Sizing:** 100% of current equity per trade.
- **Equity Risk:** ~1.0% per trade (defined by the Stop Loss distance).
- **Take Profit (TP):** 3.0%
- **Stop Loss (SL):** 1.0%
- **Trailing Stop:** 3.0x ATR (15m)

---

## Monthly Performance Breakdown

| Month | ROI | Win Rate | Sharpe | Longs | Shorts | Total Trades |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Nov 2025** | 2.54% | 42.86% | 2.70 | 4 | 10 | 14 |
| **Dec 2025** | 13.95% | 50.00% | 3.66 | 26 | 30 | 56 |
| **Jan 2026** | -0.91% | 37.25% | -0.35 | 28 | 23 | 51 |
| **Feb 2026** | 17.36% | 50.00% | 4.24 | 22 | 32 | 54 |
| **Mar 2026** | 16.11% | 47.83% | 3.19 | 38 | 31 | 69 |
| **Apr 2026** | 12.23% | 49.23% | 3.06 | 36 | 29 | 65 |
| **May 2026** | -2.51% | 26.32% | -2.05 | 16 | 22 | 38 |

---

## Key Performance Indicators
- **Average Daily Wins:** 1.36
- **Total Long Trades:** 170
- **Total Short Trades:** 177
- **Total Trades:** 347
- **Average Trade Profit:** 0.21% (Compounded)

## Conclusion
The strategy demonstrated strong performance throughout the 6-month period, successfully navigating various market regimes with a high Sharpe ratio and manageable drawdown. The highest growth was observed in February and March 2026, while the strategy effectively limited losses during the tougher conditions of January and May.
