import requests
import pandas as pd
from datetime import datetime

class TradingEngine:
    def __init__(self, db, Trade, signal_manager, ActivityLogger, SecurityEvent):
        self.db = db
        self.Trade = Trade
        self.signal_manager = signal_manager
        self.ActivityLogger = ActivityLogger
        self.SecurityEvent = SecurityEvent
    
    def get_market_data(self, pair, interval='1h', limit=100):
        """Fetch market data from Binance API"""
        try:
            symbol = pair.replace('/', '')
            url = f'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'code' in data and data['code'] == -1121:
                return None
            
            df = pd.DataFrame([{
                'timestamp': item[0],
                'open': float(item[1]),
                'high': float(item[2]),
                'low': float(item[3]),
                'close': float(item[4]),
                'volume': float(item[5]),
                'close_time': item[6]
            } for item in data])

            return df
            
        except Exception as e:
            self._log_error(f"Market data error for {pair}: {str(e)}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_ema(self, prices, period):
        """Calculate EMA indicator"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def check_condition(self, signal):
        """Check if signal conditions are met"""
        try:
            market_data = self.get_market_data(signal.pair)
            if market_data is None or len(market_data) < 50:
                return False
            
            close_prices = market_data['close']
            current_price = close_prices.iloc[-1]
            
            # Calculate indicators
            rsi = self.calculate_rsi(close_prices)
            ema_20 = self.calculate_ema(close_prices, 20)
            ema_50 = self.calculate_ema(close_prices, 50)
            macd, signal_line, hist = self.calculate_macd(close_prices)
            
            current_rsi = rsi.iloc[-1]
            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]
            current_macd = macd.iloc[-1]
            current_signal = signal_line.iloc[-1]

            if pd.isna(current_rsi):
                return False
            
            # Parse condition string
            condition = signal.entry_condition.lower()
            
            # Check BUY conditions
            if signal.signal_type == 'BUY':
                conditions_met = 0
                
                if 'rsi' in condition:
                    if 'rsi < 30' in condition and current_rsi < 30:
                        conditions_met += 1
                    elif 'rsi > 70' in condition and current_rsi > 70:
                        conditions_met += 1
                
                if 'ema' in condition:
                    if 'ema crossover' in condition and current_ema_20 > current_ema_50:
                        conditions_met += 1
                
                if 'macd' in condition:
                    if 'macd bullish' in condition and current_macd > current_signal:
                        conditions_met += 1
                
                # If any condition met (or all conditions if specified)
                required_conditions = 1
                if 'and' in condition:
                    required_conditions = condition.count('and') + 1
                
                if conditions_met >= required_conditions:
                    signal.entry_price = current_price
                    return True
            
            # Check SELL conditions
            elif signal.signal_type == 'SELL':
                conditions_met = 0
                
                if 'rsi' in condition:
                    if 'rsi > 70' in condition and current_rsi > 70:
                        conditions_met += 1
                
                if 'ema' in condition:
                    if 'ema crossover' in condition and current_ema_20 < current_ema_50:
                        conditions_met += 1
                
                if 'macd' in condition:
                    if 'macd bearish' in condition and current_macd < current_signal:
                        conditions_met += 1
                
                required_conditions = 1
                if 'and' in condition:
                    required_conditions = condition.count('and') + 1
                
                if conditions_met >= required_conditions:
                    signal.entry_price = current_price
                    return True
            
            return False
            
        except Exception as e:
            self._log_error(f"Condition check error: {str(e)}")
            return False
    
    def execute_strategy(self):
        """Run automated strategy to generate signals"""
        try:
            pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            
            for pair in pairs:
                market_data = self.get_market_data(pair)
                if market_data is None or len(market_data) < 50:
                    continue
                
                close_prices = market_data['close']
                rsi = self.calculate_rsi(close_prices)
                ema_20 = self.calculate_ema(close_prices, 20)
                ema_50 = self.calculate_ema(close_prices, 50)
                macd, signal_line, hist = self.calculate_macd(close_prices)
                
                current_rsi = rsi.iloc[-1]
                previous_rsi = rsi.iloc[-2]
                current_ema_20 = ema_20.iloc[-1]
                current_ema_50 = ema_50.iloc[-1]
                current_macd = macd.iloc[-1]
                previous_macd = macd.iloc[-2]
                current_signal = signal_line.iloc[-1]

                if pd.isna(current_rsi) or pd.isna(previous_rsi):
                    continue
                
                # BUY signal conditions
                buy_conditions = (
                    (current_rsi < 30 and previous_rsi < 30) or
                    (current_ema_20 > current_ema_50) or
                    (current_macd > current_signal and previous_macd <= current_signal)
                )
                
                # SELL signal conditions
                sell_conditions = (
                    (current_rsi > 70 and previous_rsi > 70) or
                    (current_ema_20 < current_ema_50) or
                    (current_macd < current_signal and previous_macd >= current_signal)
                )
                
                if buy_conditions:
                    # Check if signal already exists
                    existing = self.Trade.query.filter_by(
                        pair=pair,
                        signal_type='BUY',
                        status='pending'
                    ).first()
                    
                    if not existing:
                        self.signal_manager.create_auto_signal(
                            pair, 'BUY', 
                            f"RSI: {current_rsi:.2f}, EMA Crossover: {current_ema_20:.2f} > {current_ema_50:.2f}"
                        )
                
                elif sell_conditions:
                    existing = self.Trade.query.filter_by(
                        pair=pair,
                        signal_type='SELL',
                        status='pending'
                    ).first()
                    
                    if not existing:
                        self.signal_manager.create_auto_signal(
                            pair, 'SELL',
                            f"RSI: {current_rsi:.2f}, EMA Crossover: {current_ema_20:.2f} < {current_ema_50:.2f}"
                        )
        
        except Exception as e:
            self._log_error(f"Strategy execution error: {str(e)}")
    
    def _log_error(self, message):
        event = self.SecurityEvent(
            event_type='SYSTEM_ERROR',
            severity='warning',
            description=message,
            timestamp=datetime.utcnow()
        )
        self.db.session.add(event)
        self.db.session.commit()
