from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
import abc

# Base for SQLAlchemy models
Base = declarative_base()

class BaseModel(Base):
    """
    Abstract base model with common fields for all models
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Repository(abc.ABC):
    """
    Abstract base class for repository pattern
    This allows switching between different database implementations
    """
    
    @abc.abstractmethod
    def get(self, id: int):
        pass
    
    @abc.abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100):
        pass
    
    @abc.abstractmethod
    def create(self, obj):
        pass
    
    @abc.abstractmethod
    def update(self, id: int, obj):
        pass
    
    @abc.abstractmethod
    def delete(self, id: int):
        pass

# MongoDB implementation (bonus feature)
class MongoDBRepository(Repository):
    """
    MongoDB implementation of the repository pattern
    This demonstrates how to switch to MongoDB without changing business logic
    """
    
    def __init__(self, collection):
        self.collection = collection
    
    def get(self, id: int):
        # MongoDB implementation would go here
        pass
    
    def get_all(self, skip: int = 0, limit: int = 100):
        # MongoDB implementation would go here
        pass
    
    def create(self, obj):
        # MongoDB implementation would go here
        pass
    
    def update(self, id: int, obj):
        # MongoDB implementation would go here
        pass
    
    def delete(self, id: int):
        # MongoDB implementation would go here
        pass
