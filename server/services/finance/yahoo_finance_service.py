import logging
import yfinance as yf
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class StockData:
    """Container for stock data"""
    symbol: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    timestamp: datetime


@dataclass
class HistoricalData:
    """Container for historical data"""
    symbol: str
    dates: List[str]
    prices: List[float]
    volumes: List[int]
    period: str


class YahooFinanceService:
    """
    Service for fetching real-time and historical financial data from Yahoo Finance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_stock_info(self, symbol: str) -> Optional[StockData]:
        """Get current stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and change
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2]
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            stock_data = StockData(
                symbol=symbol.upper(),
                current_price=current_price,
                change=change,
                change_percent=change_percent,
                volume=hist['Volume'].iloc[-1],
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Retrieved stock data for {symbol}")
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[HistoricalData]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            historical_data = HistoricalData(
                symbol=symbol.upper(),
                dates=[date.strftime('%Y-%m-%d') for date in hist.index],
                prices=hist['Close'].tolist(),
                volumes=hist['Volume'].tolist(),
                period=period
            )
            
            self.logger.info(f"Retrieved historical data for {symbol} ({period})")
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            data = self.get_stock_info(symbol)
            if data:
                results[symbol.upper()] = data
        return results
    
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks by name or symbol"""
        try:
            # Use yfinance's search functionality
            search_results = yf.Tickers(query)
            results = []
            
            for ticker in search_results.tickers[:10]:  # Limit to 10 results
                try:
                    info = ticker.info
                    results.append({
                        'symbol': info.get('symbol', ''),
                        'name': info.get('longName', ''),
                        'sector': info.get('sector', ''),
                        'industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap', 0)
                    })
                except:
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching stocks: {str(e)}")
            return []
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary for major indices"""
        indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']  # S&P 500, Dow Jones, NASDAQ, VIX
        summary = {}
        
        for index in indices:
            data = self.get_stock_info(index)
            if data:
                summary[index] = {
                    'current_price': data.current_price,
                    'change': data.change,
                    'change_percent': data.change_percent
                }
        
        return summary 