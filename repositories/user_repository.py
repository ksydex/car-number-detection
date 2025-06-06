from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from entities.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User) 