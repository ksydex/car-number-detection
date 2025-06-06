from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .base import Base

class CarPassage(Base):
    __tablename__ = 'car_passage'

    id = Column(BigInteger, primary_key=True)
    car_id = Column(BigInteger, ForeignKey('car.id'), nullable=False)
    passage_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    passage_type = Column(Integer, nullable=False)  # 1 for entry, 2 for exit

    car = relationship("Car", back_populates="passages")
    transaction = relationship("Transaction", back_populates="passage", uselist=False) 