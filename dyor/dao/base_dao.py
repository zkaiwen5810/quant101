"""
Data Access Object (DAO) layer for models.

This module provides a clean abstraction layer for database operations,
separating business logic from data access concerns.
"""

from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from django.db import models, transaction
from django.db.models import QuerySet, Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=models.Model)


class BaseDAO(Generic[T]):
    """
    Base DAO class providing common database operations.
    
    This class implements the Repository pattern and provides a clean interface
    for database operations without exposing Django ORM details to business logic.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the DAO with a Django model class.
        
        Args:
            model_class: The Django model class this DAO manages
        """
        self.model_class = model_class
    
    def _get_manager(self, using: Optional[str] = None):
        """
        Get the model manager with optional database routing.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            Model manager with database routing applied
        """
        if using:
            return self.model_class.objects.using(using)
        return self.model_class.objects
    
    def create(self, using: Optional[str] = None, **kwargs) -> T:
        """
        Create a new instance of the model.
        
        Args:
            using: Database to use for the operation
            **kwargs: Field values for the new instance
            
        Returns:
            The created model instance
            
        Raises:
            ValidationError: If the data is invalid
        """
        try:
            instance = self.model_class(**kwargs)
            instance.full_clean()
            instance.save(using=using)
            logger.info(f"Created {self.model_class.__name__} with id: {instance.pk}")
            return instance
        except ValidationError as e:
            logger.error(f"Validation error creating {self.model_class.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    def get_by_id(self, id_value: Any, using: Optional[str] = None) -> Optional[T]:
        """
        Retrieve a model instance by its primary key.
        
        Args:
            id_value: The primary key value
            using: Database to use for the operation
            
        Returns:
            The model instance or None if not found
        """
        try:
            return self._get_manager(using).get(pk=id_value)
        except ObjectDoesNotExist:
            logger.debug(f"{self.model_class.__name__} with id {id_value} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving {self.model_class.__name__} with id {id_value}: {e}")
            raise
    
    def get_by_field(self, field_name: str, value: Any, using: Optional[str] = None) -> Optional[T]:
        """
        Retrieve a model instance by a specific field value.
        
        Args:
            field_name: The name of the field to filter by
            value: The value to match
            using: Database to use for the operation
            
        Returns:
            The model instance or None if not found
        """
        try:
            filter_kwargs = {field_name: value}
            return self._get_manager(using).get(**filter_kwargs)
        except ObjectDoesNotExist:
            logger.debug(f"{self.model_class.__name__} with {field_name}={value} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving {self.model_class.__name__} with {field_name}={value}: {e}")
            raise
    
    def filter(self, using: Optional[str] = None, **kwargs) -> QuerySet[T]:
        """
        Filter model instances by field values.
        
        Args:
            using: Database to use for the operation
            **kwargs: Field filters
            
        Returns:
            QuerySet of matching instances
        """
        try:
            return self._get_manager(using).filter(**kwargs)
        except Exception as e:
            logger.error(f"Error filtering {self.model_class.__name__}: {e}")
            raise
    
    def filter_by_query(self, query: Q, using: Optional[str] = None) -> QuerySet[T]:
        """
        Filter model instances using Django Q objects for complex queries.
        
        Args:
            query: Django Q object containing the query conditions
            using: Database to use for the operation
            
        Returns:
            QuerySet of matching instances
        """
        try:
            return self._get_manager(using).filter(query)
        except Exception as e:
            logger.error(f"Error filtering {self.model_class.__name__} with Q object: {e}")
            raise
    
    def get_all(self, using: Optional[str] = None) -> QuerySet[T]:
        """
        Retrieve all instances of the model.
        
        Args:
            using: Database to use for the operation
            
        Returns:
            QuerySet of all instances
        """
        try:
            return self._get_manager(using).all()
        except Exception as e:
            logger.error(f"Error retrieving all {self.model_class.__name__}: {e}")
            raise
    
    def update(self, instance: T, using: Optional[str] = None, **kwargs) -> T:
        """
        Update an existing model instance.
        
        Args:
            instance: The model instance to update
            using: Database to use for the operation
            **kwargs: Field values to update
            
        Returns:
            The updated model instance
            
        Raises:
            ValidationError: If the data is invalid
        """
        try:
            for field, value in kwargs.items():
                setattr(instance, field, value)
            instance.full_clean()
            instance.save(using=using)
            logger.info(f"Updated {self.model_class.__name__} with id: {instance.pk}")
            return instance
        except ValidationError as e:
            logger.error(f"Validation error updating {self.model_class.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__}: {e}")
            raise
    
    def update_by_id(self, id_value: Any, using: Optional[str] = None, **kwargs) -> Optional[T]:
        """
        Update a model instance by its primary key.
        
        Args:
            id_value: The primary key value
            using: Database to use for the operation
            **kwargs: Field values to update
            
        Returns:
            The updated model instance or None if not found
        """
        instance = self.get_by_id(id_value, using=using)
        if instance:
            return self.update(instance, using=using, **kwargs)
        return None
    
    def delete(self, instance: T, using: Optional[str] = None) -> bool:
        """
        Delete a model instance.
        
        Args:
            instance: The model instance to delete
            using: Database to use for the operation
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            instance.delete(using=using)
            logger.info(f"Deleted {self.model_class.__name__} with id: {instance.pk}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__}: {e}")
            return False
    
    def delete_by_id(self, id_value: Any, using: Optional[str] = None) -> bool:
        """
        Delete a model instance by its primary key.
        
        Args:
            id_value: The primary key value
            using: Database to use for the operation
            
        Returns:
            True if deleted successfully, False otherwise
        """
        instance = self.get_by_id(id_value, using=using)
        if instance:
            return self.delete(instance, using=using)
        return False
    
    def exists(self, using: Optional[str] = None, **kwargs) -> bool:
        """
        Check if any instances exist matching the given criteria.
        
        Args:
            using: Database to use for the operation
            **kwargs: Field filters
            
        Returns:
            True if at least one instance exists, False otherwise
        """
        try:
            return self._get_manager(using).filter(**kwargs).exists()
        except Exception as e:
            logger.error(f"Error checking existence of {self.model_class.__name__}: {e}")
            raise
    
    def count(self, using: Optional[str] = None, **kwargs) -> int:
        """
        Count instances matching the given criteria.
        
        Args:
            using: Database to use for the operation
            **kwargs: Field filters
            
        Returns:
            Number of matching instances
        """
        try:
            return self._get_manager(using).filter(**kwargs).count()
        except Exception as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise
    
    def bulk_create(self, instances: List[T], using: Optional[str] = None, batch_size: Optional[int] = None) -> List[T]:
        """
        Create multiple instances in a single database operation.
        
        Args:
            instances: List of model instances to create
            using: Database to use for the operation
            batch_size: Optional batch size for bulk operations
            
        Returns:
            List of created instances
        """
        try:
            created_instances = self._get_manager(using).bulk_create(instances, batch_size=batch_size)
            logger.info(f"Bulk created {len(created_instances)} {self.model_class.__name__} instances")
            return created_instances
        except Exception as e:
            logger.error(f"Error bulk creating {self.model_class.__name__}: {e}")
            raise
    
    def bulk_update(self, instances: List[T], fields: List[str], using: Optional[str] = None, batch_size: Optional[int] = None) -> int:
        """
        Update multiple instances in a single database operation.
        
        Args:
            instances: List of model instances to update
            fields: List of field names to update
            using: Database to use for the operation
            batch_size: Optional batch size for bulk operations
            
        Returns:
            Number of updated instances
        """
        try:
            updated_count = self._get_manager(using).bulk_update(instances, fields, batch_size=batch_size)
            logger.info(f"Bulk updated {updated_count} {self.model_class.__name__} instances")
            return updated_count
        except Exception as e:
            logger.error(f"Error bulk updating {self.model_class.__name__}: {e}")
            raise
    
    @transaction.atomic
    def create_or_update(self, defaults: Dict[str, Any], using: Optional[str] = None, **kwargs) -> T:
        """
        Create a new instance or update an existing one.
        
        Args:
            defaults: Field values to set when creating or updating
            using: Database to use for the operation
            **kwargs: Field filters to find existing instance
            
        Returns:
            The created or updated model instance
        """
        try:
            instance, created = self._get_manager(using).get_or_create(
                defaults=defaults,
                **kwargs
            )
            if created:
                logger.info(f"Created {self.model_class.__name__} with id: {instance.pk}")
            else:
                logger.info(f"Retrieved existing {self.model_class.__name__} with id: {instance.pk}")
            return instance
        except Exception as e:
            logger.error(f"Error creating or updating {self.model_class.__name__}: {e}")
            raise
