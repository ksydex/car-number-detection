from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from .base_repository import BaseRepository
from entities.car import Car
from entities.car_passage import CarPassage

class CarRepository(BaseRepository[Car]):
    def __init__(self, session: Session):
        super().__init__(session, Car)

    def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        return self.session.query(Car).filter(func.lower(Car.license_plate) == func.lower(license_plate)).first()
    
    def get_car_with_latest_passage(self, car_id: int) -> Optional[Car]:
        """
        Находит автомобиль и его последний проезд.
        """
        latest_passage_sq = self.session.query(
            CarPassage.car_id,
            func.max(CarPassage.passage_time).label('max_time')
        ).group_by(CarPassage.car_id).subquery()

        car = self.session.query(Car).options(
            joinedload(Car.passages)
        ).join(
            latest_passage_sq, Car.id == latest_passage_sq.c.car_id
        ).join(
            CarPassage, 
            (CarPassage.car_id == Car.id) & (CarPassage.passage_time == latest_passage_sq.c.max_time)
        ).filter(Car.id == car_id).first()

        return car 