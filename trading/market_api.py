import requests
import time
import hmac
import hashlib

class MarketAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"
    
    def get_ticker_price(self, symbol):
        """Get current price for a symbol"""
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {'symbol': symbol}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def get_24hr_stats(self, symbol):
        """Get 24hr statistics"""
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {'symbol': symbol}
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None
    
    def get_order_book(self, symbol, limit=100):
        """Get order book snapshot"""
        url = f"{self.base_url}/api/v3/depth"
        params = {'symbol': symbol, 'limit': limit}
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None