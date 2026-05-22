import robin_stocks.robinhood as rh
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
import datetime
import os

# CONFIGURATION - HARDCODED
ROBINHOOD_USER = "your_email@example.com"
ROBINHOOD_PASS = "your_password"
SYMBOL = 'BTC'
RISK_PER_TRADE = 0.10 # 10% of current equity
DRY_RUN = True         # Set to False for live trading

class RobinhoodBot:
    def __init__(self):
        self.symbol = SYMBOL
        self.dry_run = DRY_RUN
        self.risk_per_trade = RISK_PER_TRADE
        self.position = None
        self.entry_price = 0
        self.sl = 0
        self.tp = 0
        self.trailing_sl = 0
        self.daily_open = 0
        self.current_qty = 0

    def login(self):
        if ROBINHOOD_USER == "your_email@example.com":
            print("Please update ROBINHOOD_USER and ROBINHOOD_PASS in the script.")
            return False
        try:
            rh.login(ROBINHOOD_USER, ROBINHOOD_PASS)
            print("Logged into Robinhood.")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def get_data(self):
        historicals = rh.crypto.get_crypto_historicals(self.symbol, interval='15min', span='week')
        df = pd.DataFrame(historicals)
        df['close_price'] = pd.to_numeric(df['close_price'])
        df['high_price'] = pd.to_numeric(df['high_price'])
        df['low_price'] = pd.to_numeric(df['low_price'])
        return df

    def update_indicators(self, df):
        macd = ta.macd(df['close_price'])
        hist_col = 'MACDh_12_26_9'
        current_macd_h = macd[hist_col].iloc[-1]
        prev_macd_h = macd[hist_col].iloc[-2]
        atr = ta.atr(df['high_price'], df['low_price'], df['close_price'], length=14)
        current_atr = atr.iloc[-1]
        return current_macd_h, prev_macd_h, current_atr

    def get_daily_open(self):
        daily = rh.crypto.get_crypto_historicals(self.symbol, interval='day', span='week')
        return float(daily[-1]['open_price'])

    def get_balance(self):
        if self.dry_run: return 1000.0
        return float(rh.account.load_phoenix_account(info='crypto')['crypto_buying_power']['amount'])

    def execute_trade(self, side, amount_usd=None, qty=None):
        if self.dry_run:
            print(f"[DRY RUN] Would {side} USD:{amount_usd} QTY:{qty} of {self.symbol}")
            return 1.0
        try:
            if side == 'buy':
                res = rh.orders.order_buy_crypto_by_price(self.symbol, amount_usd)
                return float(res['quantity'])
            else:
                rh.orders.order_sell_crypto_by_quantity(self.symbol, qty)
                return 0
        except Exception as e:
            print(f"Order failed: {e}")
            return 0

    def run(self):
        if not self.login(): return
        print(f"Starting bot for {self.symbol} (Dry Run: {self.dry_run})")
        self.daily_open = self.get_daily_open()
        print(f"Initial Daily Open: {self.daily_open}")

        while True:
            try:
                now = datetime.datetime.now(datetime.UTC)
                if now.hour == 0 and now.minute < 2:
                    self.daily_open = self.get_daily_open()
                    print(f"Daily Open updated: {self.daily_open}")

                df = self.get_data()
                curr_h, prev_h, curr_atr = self.update_indicators(df)
                curr_price = float(rh.crypto.get_crypto_quote(self.symbol)['mark_price'])

                if self.position is None:
                    if now.hour < 12:
                        macd_slope_up = curr_h > prev_h
                        if curr_price > self.daily_open and macd_slope_up and curr_h > 0:
                            print(f"ENTRY LONG @ {curr_price}")
                            balance = self.get_balance()
                            trade_usd = balance * self.risk_per_trade
                            self.current_qty = self.execute_trade('buy', amount_usd=trade_usd)
                            if self.current_qty > 0:
                                self.position = 'long'
                                self.entry_price = curr_price
                                self.sl = curr_price * 0.99
                                self.tp = curr_price * 1.03
                                self.trailing_sl = self.sl
                else:
                    exit_reason = None
                    if self.position == 'long':
                        if curr_price > self.entry_price:
                            potential_tsl = curr_price - (curr_atr * 3.0)
                            if potential_tsl > self.trailing_sl:
                                self.trailing_sl = potential_tsl
                                print(f"TSL updated: {self.trailing_sl}")
                        if curr_price >= self.tp: exit_reason = "TP"
                        elif curr_price <= self.trailing_sl: exit_reason = "TSL"
                        elif curr_price <= self.sl: exit_reason = "SL"
                    if now.hour == 23 and now.minute >= 45: exit_reason = "EOD"
                    if exit_reason:
                        print(f"EXIT {self.position} via {exit_reason} @ {curr_price}")
                        self.execute_trade('sell', qty=self.current_qty)
                        self.position = None
                time.sleep(15)
            except Exception as e:
                print(f"Error in loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = RobinhoodBot()
    bot.run()
