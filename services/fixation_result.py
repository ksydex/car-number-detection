from dataclasses import dataclass
from typing import Optional

from entities.user import User
from .passage_enums import PassageResult

@dataclass
class FixationResult:
    """
    Представляет результат операции фиксации проезда.
    """
    status: PassageResult
    user: Optional[User] = None 