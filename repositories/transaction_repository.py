from sqlalchemy.orm import Session
from .base_repository import BaseRepository
from entities.transaction import Transaction

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session):
        super().__init__(session, Transaction) 