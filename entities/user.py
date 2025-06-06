from sqlalchemy import Column, BigInteger, String, Numeric
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    patronymic = Column(String(50))
    card_number = Column(String(20), nullable=False, unique=True)
    balance = Column(Numeric(10, 2), nullable=False, default=0.00)

    cars = relationship("Car", back_populates="owner") 