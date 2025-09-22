"""
DAO for EqBasic model - Stock Basic Information.

This module provides specialized data access operations for stock basic information,
including business-specific queries and operations.
"""

from typing import List, Optional, Dict, Any
from django.db.models import Q, QuerySet
from datetime import date
from .base_dao import BaseDAO
from ..models.basic import EqBasic


class EqBasicDAO(BaseDAO[EqBasic]):
    """
    Data Access Object for EqBasic model.
    
    Provides specialized methods for stock basic information operations
    beyond the standard CRUD operations from BaseDAO.
    """
    
    def __init__(self):
        super().__init__(EqBasic)
    
    def get_by_ticker(self, ticker: str, using: Optional[str] = None) -> Optional[EqBasic]:
        """
        Retrieve stock basic information by ticker symbol.
        
        Args:
            ticker: The ticker symbol (e.g., '000001.SZ')
            using: Database to use for the operation
            
        Returns:
            EqBasic instance or None if not found
        """
        return self.get_by_field('ticker', ticker, using=using)
    
    def get_by_code(self, code: str, using: Optional[str] = None) -> Optional[EqBasic]:
        """
        Retrieve stock basic information by stock code.
        
        Args:
            code: The stock code (e.g., '000001')
            using: Database to use for the operation
            
        Returns:
            EqBasic instance or None if not found
        """
        return self.get_by_field('code', code, using=using)
    
    def get_by_name(self, name: str, using: Optional[str] = None) -> Optional[EqBasic]:
        """
        Retrieve stock basic information by stock name.
        
        Args:
            name: The stock name
            using: Database to use for the operation
            
        Returns:
            EqBasic instance or None if not found
        """
        return self.get_by_field('name', name, using=using)
    
    def get_listed_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve all currently listed stocks.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of listed stocks
        """
        return self.filter(using=using, list_status='L')
    
    def get_delisted_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve all delisted stocks.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of delisted stocks
        """
        return self.filter(using=using, list_status='D')
    
    def get_suspended_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve all suspended stocks.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of suspended stocks
        """
        return self.filter(using=using, list_status='P')
    
    def get_by_industry(self, industry: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks by industry.
        
        Args:
            industry: The industry name
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks in the specified industry
        """
        return self.filter(using=using, industry=industry)
    
    def get_by_market(self, market: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks by market type.
        
        Args:
            market: The market type (e.g., '主板', '创业板', '科创板')
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks in the specified market
        """
        return self.filter(using=using, market=market)
    
    def get_by_exchange(self, exchange: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks by exchange.
        
        Args:
            exchange: The exchange code (e.g., 'SSE', 'SZSE')
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks on the specified exchange
        """
        return self.filter(using=using, exchange=exchange)
    
    def get_hs_connect_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks eligible for Shanghai-Shenzhen-Hong Kong Stock Connect.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks eligible for Stock Connect
        """
        return self.filter_by_query(Q(is_hs='H') | Q(is_hs='S'), using=using)
    
    def get_shanghai_connect_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks eligible for Shanghai Stock Connect.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks eligible for Shanghai Connect
        """
        return self.filter(using=using, is_hs='H')
    
    def get_shenzhen_connect_stocks(self, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks eligible for Shenzhen Stock Connect.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks eligible for Shenzhen Connect
        """
        return self.filter(using=using, is_hs='S')
    
    def get_stocks_listed_after(self, list_date: date, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks listed after a specific date.
        
        Args:
            list_date: The listing date threshold
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks listed after the specified date
        """
        return self.filter(using=using, list_date__gt=list_date)
    
    def get_stocks_listed_before(self, list_date: date, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks listed before a specific date.
        
        Args:
            list_date: The listing date threshold
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks listed before the specified date
        """
        return self.filter(using=using, list_date__lt=list_date)
    
    def get_stocks_by_listing_period(self, start_date: date, end_date: date, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks listed within a specific date range.
        
        Args:
            start_date: The start date of the listing period
            end_date: The end date of the listing period
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks listed within the specified period
        """
        return self.filter(using=using, list_date__gte=start_date, list_date__lte=end_date)
    
    def search_by_name_or_code(self, search_term: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Search stocks by name or code containing the search term.
        
        Args:
            search_term: The term to search for
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks matching the search term
        """
        query = Q(name__icontains=search_term) | Q(code__icontains=search_term)
        return self.filter_by_query(query, using=using)
    
    def get_stocks_by_currency(self, currency: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks by trading currency.
        
        Args:
            currency: The trading currency (e.g., 'CNY', 'USD')
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks with the specified currency
        """
        return self.filter(using=using, curr_type=currency)
    
    def get_stocks_by_region(self, region: str, using: Optional[str] = None) -> QuerySet[EqBasic]:
        """
        Retrieve stocks by region.
        
        Args:
            region: The region name
            using: Database to use for the operation
            
        Returns:
            QuerySet of stocks in the specified region
        """
        return self.filter(using=using, area=region)
    
    def get_industries(self, using: Optional[str] = None) -> List[str]:
        """
        Get a list of all unique industries.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            List of unique industry names
        """
        return list(self._get_manager(using).values_list('industry', flat=True).distinct().exclude(industry__isnull=True))
    
    def get_markets(self, using: Optional[str] = None) -> List[str]:
        """
        Get a list of all unique market types.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            List of unique market types
        """
        return list(self._get_manager(using).values_list('market', flat=True).distinct().exclude(market__isnull=True))
    
    def get_exchanges(self, using: Optional[str] = None) -> List[str]:
        """
        Get a list of all unique exchanges.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            List of unique exchange codes
        """
        return list(self._get_manager(using).values_list('exchange', flat=True).distinct().exclude(exchange__isnull=True))
    
    def get_regions(self, using: Optional[str] = None) -> List[str]:
        """
        Get a list of all unique regions.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            List of unique region names
        """
        return list(self._get_manager(using).values_list('area', flat=True).distinct().exclude(area__isnull=True))
    
    def get_currencies(self, using: Optional[str] = None) -> List[str]:
        """
        Get a list of all unique trading currencies.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            List of unique currency codes
        """
        return list(self._get_manager(using).values_list('curr_type', flat=True).distinct().exclude(curr_type__isnull=True))
    
    def get_stock_statistics(self, using: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive statistics about stocks.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            Dictionary containing various stock statistics
        """
        total_stocks = self.count(using=using)
        listed_stocks = self.count(using=using, list_status='L')
        delisted_stocks = self.count(using=using, list_status='D')
        suspended_stocks = self.count(using=using, list_status='P')
        
        hs_connect_stocks = self.count(using=using, is_hs__in=['H', 'S'])
        shanghai_connect = self.count(using=using, is_hs='H')
        shenzhen_connect = self.count(using=using, is_hs='S')
        
        return {
            'total_stocks': total_stocks,
            'listed_stocks': listed_stocks,
            'delisted_stocks': delisted_stocks,
            'suspended_stocks': suspended_stocks,
            'hs_connect_eligible': hs_connect_stocks,
            'shanghai_connect_eligible': shanghai_connect,
            'shenzhen_connect_eligible': shenzhen_connect,
            'industries_count': len(self.get_industries(using=using)),
            'markets_count': len(self.get_markets(using=using)),
            'exchanges_count': len(self.get_exchanges(using=using)),
            'regions_count': len(self.get_regions(using=using)),
            'currencies_count': len(self.get_currencies(using=using))
        }
    
    def bulk_upsert_stocks(self, stock_data: List[Dict[str, Any]], using: Optional[str] = None) -> List[EqBasic]:
        """
        Bulk upsert stock basic information.
        
        Args:
            stock_data: List of dictionaries containing stock data
            using: Database to use for the operation
            
        Returns:
            List of created or updated EqBasic instances
        """
        instances = []
        for data in stock_data:
            ticker = data.get('ticker')
            if not ticker:
                continue
                
            instance, created = self._get_manager(using).get_or_create(
                ticker=ticker,
                defaults=data
            )
            instances.append(instance)
        
        return instances
