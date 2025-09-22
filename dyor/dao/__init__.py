"""
DAO (Data Access Object) package for models.

This package contains all DAO classes that provide a clean abstraction layer
for database operations, separating business logic from data access concerns.
"""

from .base_dao import BaseDAO
from .eq_basic_dao import EqBasicDAO
from .eq_daily_px_dao import EqDailyPxDAO

# Create singleton instances for easy access
eq_basic_dao = EqBasicDAO()
eq_daily_px_dao = EqDailyPxDAO()

# Export all DAO classes and instances
__all__ = [
    # DAO Classes
    'BaseDAO',
    'EqBasicDAO', 
    'EqDailyPxDAO',
    
    # DAO Instances
    'eq_basic_dao',
    'eq_daily_px_dao',
]
