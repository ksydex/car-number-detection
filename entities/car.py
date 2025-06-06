from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Car(Base):
    __tablename__ = 'car'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    license_plate = Column(String(9), nullable=False, unique=True)

    owner = relationship("User", back_populates="cars")
    passages = relationship("CarPassage", back_populates="car") 