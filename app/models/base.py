from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
import abc

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Repository(abc.ABC):
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
