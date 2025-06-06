from typing import Optional
from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from entities.car_passage import CarPassage

class CarPassageRepository(BaseRepository[CarPassage]):
    def __init__(self, session: Session):
        super().__init__(session, CarPassage)

    def find_latest_by_car_id(self, car_id: int) -> Optional[CarPassage]:
        return self.session.query(CarPassage).filter(
            CarPassage.car_id == car_id
        ).order_by(CarPassage.passage_time.desc()).first() 