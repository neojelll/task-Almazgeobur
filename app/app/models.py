from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Date,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))
    category = Column(String)
    date = Column(Date)

    task = relationship('Task', back_populates='products')


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    hash_file = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now())

    llm_response = relationship('LLMResponse', back_populates='task', uselist=False)
    products = relationship('Product', back_populates='task')


class LLMResponse(Base):
    __tablename__ = 'llm_responses'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    response = Column(Text, nullable=False)

    task = relationship('Task', back_populates='llm_response')
