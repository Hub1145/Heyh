import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import datetime
import time
import os

def fetch_data(symbol='BTC/USDT', days=180):
    """
    Fetches historical OHLCV data from Binance US (reachable from this environment).
    """
    exchange = ccxt.binanceus()
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=days)
    since = int(six_months_ago.timestamp() * 1000)

    def fetch_timeframe(tf, limit=1000):
        print(f"Fetching {tf} data...")
        all_ohlcv = []
        current_since = since
        while current_since < exchange.milliseconds():
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, tf, current_since, limit)
                if len(ohlcv) == 0: break
                all_ohlcv.extend(ohlcv)
                current_since = ohlcv[-1][0] + 1
                time.sleep(exchange.rateLimit / 1000)
                if tf == '15m' and len(all_ohlcv) > 20000: break
            except Exception as e:
                print(f"Error: {e}")
                break
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    df_1d = fetch_timeframe('1d')
    df_15m = fetch_timeframe('15m')
    return df_1d, df_15m

def run_backtest(df_1d, df_15m, tp_pct=0.03, sl_pct=0.01, trailing_atr_mult=3.5):
    # Prepare Indicators
    df_1d['date'] = df_1d['timestamp'].dt.date
    daily_info = df_1d[['date', 'open']].rename(columns={'open': 'daily_open'})

    macd_fast, macd_slow, macd_signal = 12, 21, 9
    macd = ta.macd(df_15m['close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    df_15m = pd.concat([df_15m, macd], axis=1)
    hist_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'
    df_15m['atr15m'] = ta.atr(df_15m['high'], df_15m['low'], df_15m['close'], length=14)
    df_15m['date'] = df_15m['timestamp'].dt.date

    df = df_15m.merge(daily_info, on='date', how='left')

    trades = []
    position = None
    capital = 1.0 # Start with 1.0 (100%)

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]

        if any(pd.isna([row[hist_col], row['atr15m'], row['daily_open']])): continue

        if position:
            if position['type'] == 'long':
                # Update Trailing SL
                if row['close'] > position['entry_price']:
                    potential_trailing = row['close'] - (row['atr15m'] * trailing_atr_mult)
                    if potential_trailing > position['trailing_sl']:
                        position['trailing_sl'] = potential_trailing

                # Check Exits - PRIORITIZE TRAILING SL and TP
                # (Logic fix: check most favorable/likely exit conditions first)
                if row['high'] >= position['tp']:
                    trades.append({'pnl': tp_pct})
                    position = None
                elif row['low'] <= position['trailing_sl']:
                    # If trailing_sl > sl, it's a profit or reduced loss
                    pnl = (position['trailing_sl'] - position['entry_price']) / position['entry_price']
                    trades.append({'pnl': pnl})
                    position = None
                elif row['low'] <= position['sl']:
                    trades.append({'pnl': -sl_pct})
                    position = None
                elif row['timestamp'].hour == 23 and row['timestamp'].minute == 45:
                    pnl = (row['close'] - position['entry_price']) / position['entry_price']
                    trades.append({'pnl': pnl})
                    position = None

            elif position['type'] == 'short':
                if row['close'] < position['entry_price']:
                    potential_trailing = row['close'] + (row['atr15m'] * trailing_atr_mult)
                    if potential_trailing < position['trailing_sl']:
                        position['trailing_sl'] = potential_trailing

                if row['low'] <= position['tp']:
                    trades.append({'pnl': tp_pct})
                    position = None
                elif row['high'] >= position['trailing_sl']:
                    pnl = (position['entry_price'] - position['trailing_sl']) / position['entry_price']
                    trades.append({'pnl': pnl})
                    position = None
                elif row['high'] >= position['sl']:
                    trades.append({'pnl': -sl_pct})
                    position = None
                elif row['timestamp'].hour == 23 and row['timestamp'].minute == 45:
                    pnl = (position['entry_price'] - row['close']) / position['entry_price']
                    trades.append({'pnl': pnl})
                    position = None

        if not position:
            # ENTRY: If price is above/below Daily Open and MACD Histogram crosses 0
            if row['timestamp'].hour < 12:
                if row['close'] > row['daily_open'] and prev_row[hist_col] <= 0 and row[hist_col] > 0:
                    position = {
                        'type': 'long',
                        'entry_price': row['close'],
                        'sl': row['close'] * (1 - sl_pct),
                        'tp': row['close'] * (1 + tp_pct),
                        'trailing_sl': row['close'] * (1 - sl_pct)
                    }
                elif row['close'] < row['daily_open'] and prev_row[hist_col] >= 0 and row[hist_col] < 0:
                    position = {
                        'type': 'short',
                        'entry_price': row['close'],
                        'sl': row['close'] * (1 + sl_pct),
                        'tp': row['close'] * (1 - tp_pct),
                        'trailing_sl': row['close'] * (1 + sl_pct)
                    }

    if not trades: return 0, 0, 0, 0

    trades_df = pd.DataFrame(trades)
    # Compounding ROI
    current_cap = 1.0
    for pnl in trades_df['pnl']:
        current_cap *= (1 + pnl)
    comp_roi = current_cap - 1.0

    wr = (trades_df['pnl'] > 0).mean()
    sharpe = trades_df['pnl'].mean() / (trades_df['pnl'].std() + 1e-9) * np.sqrt(252)

    return comp_roi, wr, sharpe, len(trades_df)

if __name__ == "__main__":
    df_1d, df_15m = fetch_data()
    if not df_1d.empty and not df_15m.empty:
        roi, wr, sharpe, n = run_backtest(df_1d, df_15m)
        print("\nStrategy Performance Summary (Self-Contained Run):")
        print(f"Compounded ROI: {roi:.2%}")
        print(f"Win Rate: {wr:.2%}")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Total Trades: {n}")
    else:
        print("Failed to fetch data.")
