"""
DAO for EqDailyPx model - Daily Price Data.

This module provides specialized data access operations for daily price data,
including time-series queries and financial calculations.
"""

from typing import List, Optional, Dict, Any, Tuple
from django.db.models import Q, QuerySet, Avg, Max, Min, Sum, Count
from django.db.models.functions import TruncDate
from datetime import date, datetime, timedelta
from decimal import Decimal
from .base_dao import BaseDAO
from ..models.quote import EqDailyPx


class EqDailyPxDAO(BaseDAO[EqDailyPx]):
    """
    Data Access Object for EqDailyPx model.
    
    Provides specialized methods for daily price data operations
    including time-series analysis and financial calculations.
    """
    
    def __init__(self):
        super().__init__(EqDailyPx)
    
    def get_by_ticker_and_date(self, ticker: str, trade_date: date) -> Optional[EqDailyPx]:
        """
        Retrieve daily price data for a specific ticker and date.
        
        Args:
            ticker: The ticker symbol
            trade_date: The trading date
            
        Returns:
            EqDailyPx instance or None if not found
        """
        return self.filter(ticker=ticker, trade_date=trade_date).first()
    
    def get_by_ticker(self, ticker: str) -> QuerySet[EqDailyPx]:
        """
        Retrieve all daily price data for a specific ticker.
        
        Args:
            ticker: The ticker symbol
            
        Returns:
            QuerySet of daily price data for the ticker
        """
        return self.filter(ticker=ticker).order_by('trade_date')
    
    def get_by_date(self, trade_date: date) -> QuerySet[EqDailyPx]:
        """
        Retrieve all daily price data for a specific date.
        
        Args:
            trade_date: The trading date
            
        Returns:
            QuerySet of daily price data for the date
        """
        return self.filter(trade_date=trade_date)
    
    def get_ticker_price_range(self, ticker: str, start_date: date, end_date: date) -> QuerySet[EqDailyPx]:
        """
        Retrieve price data for a ticker within a date range.
        
        Args:
            ticker: The ticker symbol
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)
            
        Returns:
            QuerySet of price data within the date range
        """
        return self.filter(
            ticker=ticker,
            trade_date__gte=start_date,
            trade_date__lte=end_date
        ).order_by('trade_date')
    
    def get_latest_price(self, ticker: str) -> Optional[EqDailyPx]:
        """
        Get the most recent price data for a ticker.
        
        Args:
            ticker: The ticker symbol
            
        Returns:
            The most recent EqDailyPx instance or None
        """
        return self.filter(ticker=ticker).order_by('-trade_date').first()
    
    def get_earliest_price(self, ticker: str) -> Optional[EqDailyPx]:
        """
        Get the earliest price data for a ticker.
        
        Args:
            ticker: The ticker symbol
            
        Returns:
            The earliest EqDailyPx instance or None
        """
        return self.filter(ticker=ticker).order_by('trade_date').first()
    
    def get_price_statistics(self, ticker: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate price statistics for a ticker within a date range.
        
        Args:
            ticker: The ticker symbol
            start_date: Optional start date (defaults to earliest available)
            end_date: Optional end date (defaults to latest available)
            
        Returns:
            Dictionary containing price statistics
        """
        queryset = self.filter(ticker=ticker)
        
        if start_date:
            queryset = queryset.filter(trade_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(trade_date__lte=end_date)
        
        stats = queryset.aggregate(
            avg_close=Avg('close'),
            max_close=Max('close'),
            min_close=Min('close'),
            avg_volume=Avg('volume'),
            max_volume=Max('volume'),
            min_volume=Min('volume'),
            total_volume=Sum('volume'),
            total_turnover=Sum('turnover'),
            trading_days=Count('id')
        )
        
        # Calculate additional metrics
        latest_price = self.get_latest_price(ticker)
        earliest_price = self.get_earliest_price(ticker)
        
        if latest_price and earliest_price:
            total_return = ((latest_price.close - earliest_price.close) / earliest_price.close) * 100
        else:
            total_return = None
        
        return {
            'ticker': ticker,
            'period_start': start_date,
            'period_end': end_date,
            'trading_days': stats['trading_days'],
            'price_stats': {
                'avg_close': stats['avg_close'],
                'max_close': stats['max_close'],
                'min_close': stats['min_close'],
                'latest_close': latest_price.close if latest_price else None,
                'earliest_close': earliest_price.close if earliest_price else None,
                'total_return_pct': total_return
            },
            'volume_stats': {
                'avg_volume': stats['avg_volume'],
                'max_volume': stats['max_volume'],
                'min_volume': stats['min_volume'],
                'total_volume': stats['total_volume']
            },
            'turnover_stats': {
                'total_turnover': stats['total_turnover']
            }
        }
    
    def get_top_gainers(self, trade_date: date, limit: int = 10) -> QuerySet[EqDailyPx]:
        """
        Get top gaining stocks for a specific date.
        
        Args:
            trade_date: The trading date
            limit: Maximum number of results
            
        Returns:
            QuerySet of top gaining stocks
        """
        return self.filter(
            trade_date=trade_date,
            pct_chg__isnull=False
        ).order_by('-pct_chg')[:limit]
    
    def get_top_losers(self, trade_date: date, limit: int = 10) -> QuerySet[EqDailyPx]:
        """
        Get top losing stocks for a specific date.
        
        Args:
            trade_date: The trading date
            limit: Maximum number of results
            
        Returns:
            QuerySet of top losing stocks
        """
        return self.filter(
            trade_date=trade_date,
            pct_chg__isnull=False
        ).order_by('pct_chg')[:limit]
    
    def get_most_active(self, trade_date: date, limit: int = 10) -> QuerySet[EqDailyPx]:
        """
        Get most actively traded stocks by volume for a specific date.
        
        Args:
            trade_date: The trading date
            limit: Maximum number of results
            
        Returns:
            QuerySet of most active stocks
        """
        return self.filter(trade_date=trade_date).order_by('-volume')[:limit]
    
    def get_highest_turnover(self, trade_date: date, limit: int = 10) -> QuerySet[EqDailyPx]:
        """
        Get stocks with highest turnover for a specific date.
        
        Args:
            trade_date: The trading date
            limit: Maximum number of results
            
        Returns:
            QuerySet of stocks with highest turnover
        """
        return self.filter(trade_date=trade_date).order_by('-turnover')[:limit]
    
    def get_price_movements(self, ticker: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent price movements for a ticker.
        
        Args:
            ticker: The ticker symbol
            days: Number of recent days to analyze
            
        Returns:
            List of dictionaries containing price movement data
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        price_data = self.get_ticker_price_range(ticker, start_date, end_date)
        
        movements = []
        for price in price_data:
            movements.append({
                'date': price.trade_date,
                'open': price.open,
                'high': price.high,
                'low': price.low,
                'close': price.close,
                'change': price.chg,
                'change_pct': price.pct_chg,
                'volume': price.volume,
                'turnover': price.turnover
            })
        
        return movements
    
    def get_volatility_analysis(self, ticker: str, days: int = 30) -> Dict[str, Any]:
        """
        Calculate volatility metrics for a ticker.
        
        Args:
            ticker: The ticker symbol
            days: Number of days for analysis
            
        Returns:
            Dictionary containing volatility metrics
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        price_data = self.get_ticker_price_range(ticker, start_date, end_date)
        
        if not price_data.exists():
            return {'error': 'No data available for the specified period'}
        
        # Calculate daily returns
        daily_returns = []
        prev_close = None
        
        for price in price_data.order_by('trade_date'):
            if prev_close is not None:
                daily_return = ((price.close - prev_close) / prev_close) * 100
                daily_returns.append(daily_return)
            prev_close = price.close
        
        if not daily_returns:
            return {'error': 'Insufficient data for volatility calculation'}
        
        # Calculate volatility metrics
        avg_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
        volatility = variance ** 0.5
        
        return {
            'ticker': ticker,
            'period_days': days,
            'trading_days': len(daily_returns),
            'avg_daily_return': avg_return,
            'volatility': volatility,
            'max_daily_return': max(daily_returns),
            'min_daily_return': min(daily_returns),
            'positive_days': sum(1 for r in daily_returns if r > 0),
            'negative_days': sum(1 for r in daily_returns if r < 0)
        }
    
    def get_market_summary(self, trade_date: date) -> Dict[str, Any]:
        """
        Get market summary statistics for a specific date.
        
        Args:
            trade_date: The trading date
            
        Returns:
            Dictionary containing market summary
        """
        daily_data = self.get_by_date(trade_date)
        
        if not daily_data.exists():
            return {'error': 'No data available for the specified date'}
        
        # Calculate market-wide statistics
        market_stats = daily_data.aggregate(
            total_stocks=Count('id'),
            avg_change_pct=Avg('pct_chg'),
            stocks_up=Count('id', filter=Q(pct_chg__gt=0)),
            stocks_down=Count('id', filter=Q(pct_chg__lt=0)),
            stocks_unchanged=Count('id', filter=Q(pct_chg=0)),
            total_volume=Sum('volume'),
            total_turnover=Sum('turnover'),
            avg_volume=Avg('volume')
        )
        
        # Get top movers
        top_gainers = self.get_top_gainers(trade_date, 5)
        top_losers = self.get_top_losers(trade_date, 5)
        most_active = self.get_most_active(trade_date, 5)
        
        return {
            'date': trade_date,
            'market_overview': {
                'total_stocks': market_stats['total_stocks'],
                'avg_change_pct': market_stats['avg_change_pct'],
                'stocks_up': market_stats['stocks_up'],
                'stocks_down': market_stats['stocks_down'],
                'stocks_unchanged': market_stats['stocks_unchanged']
            },
            'volume_overview': {
                'total_volume': market_stats['total_volume'],
                'avg_volume': market_stats['avg_volume'],
                'total_turnover': market_stats['total_turnover']
            },
            'top_gainers': [
                {
                    'ticker': px.ticker,
                    'change_pct': px.pct_chg,
                    'close': px.close
                } for px in top_gainers
            ],
            'top_losers': [
                {
                    'ticker': px.ticker,
                    'change_pct': px.pct_chg,
                    'close': px.close
                } for px in top_losers
            ],
            'most_active': [
                {
                    'ticker': px.ticker,
                    'volume': px.volume,
                    'turnover': px.turnover
                } for px in most_active
            ]
        }
    
    def bulk_upsert_prices(self, price_data: List[Dict[str, Any]]) -> List[EqDailyPx]:
        """
        Bulk upsert daily price data.
        
        Args:
            price_data: List of dictionaries containing price data
            
        Returns:
            List of created or updated EqDailyPx instances
        """
        instances = []
        for data in price_data:
            ticker = data.get('ticker')
            trade_date = data.get('trade_date')
            
            if not ticker or not trade_date:
                continue
            
            instance, created = self.model_class.objects.get_or_create(
                ticker=ticker,
                trade_date=trade_date,
                defaults=data
            )
            instances.append(instance)
        
        return instances
    
    def get_missing_dates(self, ticker: str, start_date: date, end_date: date) -> List[date]:
        """
        Find missing trading dates for a ticker within a date range.
        
        Args:
            ticker: The ticker symbol
            start_date: The start date
            end_date: The end date
            
        Returns:
            List of missing dates
        """
        existing_dates = set(
            self.filter(ticker=ticker, trade_date__gte=start_date, trade_date__lte=end_date)
            .values_list('trade_date', flat=True)
        )
        
        all_dates = set()
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                all_dates.add(current_date)
            current_date += timedelta(days=1)
        
        return sorted(all_dates - existing_dates)
