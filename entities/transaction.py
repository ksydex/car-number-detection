from sqlalchemy import Column, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(BigInteger, primary_key=True)
    passage_id = Column(BigInteger, ForeignKey('car_passage.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    passage = relationship("CarPassage", back_populates="transaction") 