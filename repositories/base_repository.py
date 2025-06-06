from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from entities.base import Base

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get(self, id: int) -> Optional[T]:
        return self.session.query(self.model).get(id)

    def get_all(self) -> List[T]:
        return self.session.query(self.model).all()

    def create(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def update(self, entity: T) -> T:
        self.session.merge(entity)
        return entity

    def delete(self, entity: T):
        self.session.delete(entity) 