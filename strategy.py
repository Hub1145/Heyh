import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import datetime
import time
import os

def fetch_data(symbol='BTC/USDT', days=180):
    exchange = ccxt.binanceus()
    since = int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp() * 1000)
    def fetch_tf(tf):
        all_ohlcv = []
        curr = since
        while curr < exchange.milliseconds():
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, tf, curr, 1000)
                if not ohlcv: break
                all_ohlcv.extend(ohlcv)
                curr = ohlcv[-1][0] + 1
                time.sleep(exchange.rateLimit / 1000)
                if tf == '15m' and len(all_ohlcv) > 20000: break
            except: break
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    return fetch_tf('1d'), fetch_tf('15m')

def run_backtest(df_1d, df_15m, tp_pct=0.03, sl_pct=0.01, trailing_mult=3.0):
    df_1d['date'] = df_1d['timestamp'].dt.date
    daily_info = df_1d[['date', 'open']].rename(columns={'open': 'daily_open'})
    macd = ta.macd(df_15m['close'])
    df_15m = pd.concat([df_15m, macd], axis=1)
    hist_col = 'MACDh_12_26_9'
    df_15m['atr15m'] = ta.atr(df_15m['high'], df_15m['low'], df_15m['close'], length=14)
    df_15m['date'] = df_15m['timestamp'].dt.date
    df = df_15m.merge(daily_info, on='date', how='left')
    trades = []
    position = None
    balance = 1000.0
    initial_balance = 1000.0
    risk_pct = 1.0
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        if any(pd.isna([row['daily_open'], row[hist_col]])): continue
        if position:
            epnl = None
            if position['type'] == 'long':
                if row['close'] > position['entry_price']:
                    pot_tsl = row['close'] - (row['atr15m'] * trailing_mult)
                    if pot_tsl > position['trailing_sl']: position['trailing_sl'] = pot_tsl
                if row['high'] >= position['tp']: epnl = tp_pct
                elif row['low'] <= position['trailing_sl']: epnl = (position['trailing_sl'] - position['entry_price'])/position['entry_price']
                elif row['low'] <= position['sl']: epnl = -sl_pct
                elif row['timestamp'].hour == 23 and row['timestamp'].minute == 45: epnl = (row['close'] - position['entry_price'])/position['entry_price']
            else:
                if row['close'] < position['entry_price']:
                    pot_tsl = row['close'] + (row['atr15m'] * trailing_mult)
                    if pot_tsl < position['trailing_sl']: position['trailing_sl'] = pot_tsl
                if row['low'] <= position['tp']: epnl = tp_pct
                elif row['high'] >= position['trailing_sl']: epnl = (position['entry_price'] - position['trailing_sl'])/position['entry_price']
                elif row['high'] >= position['sl']: epnl = -sl_pct
                elif row['timestamp'].hour == 23 and row['timestamp'].minute == 45: epnl = (position['entry_price'] - row['close'])/position['entry_price']
            if epnl is not None:
                balance += balance * risk_pct * epnl
                trades.append({'pnl': epnl, 'type': position['type'], 'date': row['date']})
                position = None
        if not position:
             if prev_row['close'] < row['daily_open'] and row['high'] >= row['daily_open'] and row[hist_col] > prev_row[hist_col] and row[hist_col] > 0:
                 position = {'type': 'long', 'entry_price': row['daily_open'], 'sl': row['daily_open']*(1-sl_pct), 'tp': row['daily_open']*(1+tp_pct), 'trailing_sl': row['daily_open']*(1-sl_pct)}
             elif prev_row['close'] > row['daily_open'] and row['low'] <= row['daily_open'] and row[hist_col] < prev_row[hist_col] and row[hist_col] < 0:
                 position = {'type': 'short', 'entry_price': row['daily_open'], 'sl': row['daily_open']*(1+sl_pct), 'tp': row['daily_open']*(1-tp_pct), 'trailing_sl': row['daily_open']*(1+sl_pct)}
    if not trades: return
    tdf = pd.DataFrame(trades)
    print(f"\nStats:\nStarting Balance: ${initial_balance}\nEnding Balance: ${balance:.2f}\nROI: {(balance-initial_balance)/initial_balance:.2%}\nWR: {(tdf['pnl']>0).mean():.2%}\nLongs: {(tdf['type']=='long').sum()}\nShorts: {(tdf['type']=='short').sum()}\nAvg Daily Wins: {tdf[tdf['pnl']>0].groupby('date').size().mean():.2f}")

if __name__ == "__main__":
    d1, d15 = fetch_data()
    run_backtest(d1, d15)
