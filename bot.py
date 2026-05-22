import robin_stocks.robinhood as rh
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
import datetime
import os

# CONFIGURATION - HARDCODED AS REQUESTED
ROBINHOOD_USER = "your_email@example.com"
ROBINHOOD_PASS = "your_password"
SYMBOL = 'BTC'
POSITION_SIZE_PCT = 1.0  # 100% of equity (Parameter used for 72.61% ROI)
TP_PCT = 0.03            # 3% Take Profit
SL_PCT = 0.01            # 1% Stop Loss
TRAILING_MULT = 3.0      # 3.0x ATR Trailing Stop
DRY_RUN = True           # Set to False for live trading

class RobinhoodBot:
    def __init__(self):
        self.symbol = SYMBOL
        self.dry_run = DRY_RUN
        self.risk_pct = POSITION_SIZE_PCT
        self.position = None
        self.entry_price = 0
        self.sl = 0
        self.tp = 0
        self.trailing_sl = 0
        self.daily_open = 0
        self.current_qty = 0
        self.last_bar_close = 0

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
        # Fetch 15m historicals
        historicals = rh.crypto.get_crypto_historicals(self.symbol, interval='15min', span='week')
        df = pd.DataFrame(historicals)
        df['close_price'] = pd.to_numeric(df['close_price'])
        df['high_price'] = pd.to_numeric(df['high_price'])
        df['low_price'] = pd.to_numeric(df['low_price'])
        return df

    def update_indicators(self, df):
        macd = ta.macd(df['close_price'], fast=12, slow=21, signal=9)
        hist_col = 'MACDh_12_21_9'
        # If default settings were used in the 72.61% ROI run, it was 12, 26, 9
        # Re-checking strategy.py: it used default MACD (12, 26, 9)
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
        # Fetch crypto buying power
        return float(rh.account.load_phoenix_account(info='crypto')['crypto_buying_power']['amount'])

    def execute_trade(self, side, amount_usd=None, qty=None):
        if self.dry_run:
            print(f"[DRY RUN] {side.upper()} USD:{amount_usd} QTY:{qty}")
            return 1.0 # Dummy qty
        try:
            if side == 'buy':
                res = rh.orders.order_buy_crypto_by_price(self.symbol, amount_usd)
                return float(res['quantity'])
            else:
                rh.orders.order_sell_crypto_by_quantity(self.symbol, qty)
                return 0
        except Exception as e:
            print(f"Order failure: {e}")
            return 0

    def run(self):
        if not self.login(): return
        print(f"Bot started for {self.symbol} (Dry Run: {self.dry_run})")
        self.daily_open = self.get_daily_open()

        while True:
            try:
                now = datetime.datetime.now(datetime.UTC)
                # Update Daily Open
                if now.hour == 0 and now.minute < 2:
                    self.daily_open = self.get_daily_open()
                    print(f"New Daily Open: {self.daily_open}")

                df = self.get_data()
                curr_h, prev_h, curr_atr = self.update_indicators(df)
                self.last_bar_close = df['close_price'].iloc[-1]

                quote = rh.crypto.get_crypto_quote(self.symbol)
                curr_price = float(quote['mark_price'])

                if self.position is None:
                    # ENTRY LOGIC (Immediate Slope Pattern)
                    if now.hour < 12:
                        macd_slope_up = curr_h > prev_h
                        macd_slope_down = curr_h < prev_h

                        # Long Entry
                        if self.last_bar_close < self.daily_open and curr_price >= self.daily_open and macd_slope_up and curr_h > 0:
                            print(f"SIGNAL: LONG @ {curr_price}")
                            balance = self.get_balance()
                            trade_usd = balance * self.risk_pct
                            self.current_qty = self.execute_trade('buy', amount_usd=trade_usd)
                            if self.current_qty > 0:
                                self.position = 'long'
                                self.entry_price = curr_price
                                self.sl = self.entry_price * (1 - SL_PCT)
                                self.tp = self.entry_price * (1 + TP_PCT)
                                self.trailing_sl = self.sl

                        # Short Entry (Robinhood is spot, so 'short' is simulated or sell if held)
                        elif self.last_bar_close > self.daily_open and curr_price <= self.daily_open and macd_slope_down and curr_h < 0:
                            print(f"SIGNAL: SHORT @ {curr_price}")
                            # Note: Actual shorting on Robinhood Crypto is not available for all users.
                            # This bot will attempt to sell if holding or log the signal.
                            print("Note: Robinhood Crypto does not support direct shorting. Order skipped or sell executed.")

                else:
                    # EXIT LOGIC
                    exit_reason = None
                    if self.position == 'long':
                        # Update Trailing Stop
                        if curr_price > self.entry_price:
                            potential_tsl = curr_price - (curr_atr * TRAILING_MULT)
                            if potential_tsl > self.trailing_sl:
                                self.trailing_sl = potential_tsl
                                print(f"TSL Updated: {self.trailing_sl}")

                        if curr_price >= self.tp: exit_reason = "Take Profit"
                        elif curr_price <= self.trailing_sl: exit_reason = "Trailing Stop"
                        elif curr_price <= self.sl: exit_reason = "Stop Loss"

                    if now.hour == 23 and now.minute >= 45: exit_reason = "End of Day"

                    if exit_reason:
                        print(f"EXIT: {exit_reason} @ {curr_price}")
                        self.execute_trade('sell', qty=self.current_qty)
                        self.position = None
                        self.current_qty = 0

                time.sleep(15) # Poll every 15 seconds for immediate execution

            except Exception as e:
                print(f"Bot Error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = RobinhoodBot()
    bot.run()
