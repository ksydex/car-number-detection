from sqlalchemy.orm import Session
from sqlalchemy import text

from repositories.car_repository import CarRepository
from repositories.car_passage_repository import CarPassageRepository
from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from entities.car_passage import CarPassage
from entities.transaction import Transaction
from services.passage_enums import PassageResult
from services.fixation_result import FixationResult
from settings import WITHDRAWAL_AMOUNT
from myutils.plate_matching import are_plates_similar

class CarPassageService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.car_repo = CarRepository(db_session)
        self.user_repo = UserRepository(db_session)
        self.passage_repo = CarPassageRepository(db_session)
        self.transaction_repo = TransactionRepository(db_session)
        self._processed_car_ids_session = set()

    def test_connection(self) -> bool:
        """
        Проверяет соединение с базой данных, выполняя простой запрос.
        Возвращает True в случае успеха, иначе False.
        """
        try:
            self.db_session.execute(text('SELECT 1'))
            print("INFO: Database connection successful.")
            return True
        except Exception as e:
            print(f"ERROR: Database connection failed: {e}")
            return False

    def fixate_car_passage(self, license_plate: str) -> FixationResult:
        all_cars = self.car_repo.get_all()
        found_car = None
        for car in all_cars:
            if are_plates_similar(car.license_plate, license_plate):
                found_car = car
                break
        
        if found_car and found_car.id in self._processed_car_ids_session:
            return FixationResult(status=PassageResult.ALREADY_PROCESSED_IN_SESSION, user=found_car.owner)

        if not found_car:
            return FixationResult(status=PassageResult.CAR_NOT_FOUND)

        latest_passage = self.passage_repo.find_latest_by_car_id(found_car.id)
        owner = found_car.owner

        # Тип проезда: 1 - въезд, 2 - выезд
        if latest_passage and latest_passage.passage_type == 1: # Последний проезд был въездом
            # Создаем запись о выезде. Это нужно в обоих случаях.
            new_passage = CarPassage(car_id=found_car.id, passage_type=2)
            self.passage_repo.create(new_passage)

            # Проверяем, есть ли владелец и достаточно ли средств для списания
            if owner and owner.balance >= WITHDRAWAL_AMOUNT:
                # Списываем деньги
                owner.balance -= WITHDRAWAL_AMOUNT
                # Создаем транзакцию, связывая её с проездом через relationship
                new_transaction = Transaction(amount=WITHDRAWAL_AMOUNT, passage=new_passage)
                self.transaction_repo.create(new_transaction)
                
                self.db_session.commit()
                self._processed_car_ids_session.add(found_car.id)
                return FixationResult(status=PassageResult.DEPARTURE_WITH_MONEY_WITHDRAW, user=owner)
            else:
                # Средств недостаточно или нет владельца. Фиксируем только выезд.
                self.db_session.commit()
                self._processed_car_ids_session.add(found_car.id)
                return FixationResult(status=PassageResult.DEPARTURE_USER_NO_MONEY, user=owner)
        else: # Если проездов не было или последний был выездом
            # Создаем запись о въезде
            new_passage = CarPassage(car_id=found_car.id, passage_type=1)
            self.passage_repo.create(new_passage)
            self.db_session.commit()
            self._processed_car_ids_session.add(found_car.id)
            return FixationResult(status=PassageResult.ARRIVAL, user=owner) 