SIMILARITY_THRESHOLD = 0.7

# Словарь для транслитерации визуально схожих символов
# Используются только те буквы, которые разрешены в российских номерах
CHAR_MAP = {
    'A': 'А', 'B': 'В', 'E': 'Е', 'K': 'К', 'M': 'М', 'H': 'Н',
    'O': 'О', 'P': 'Р', 'C': 'С', 'T': 'Т', 'Y': 'У', 'X': 'Х'
}

def _normalize_plate(plate: str) -> str:
    """
    Приводит номерной знак к единому формату:
    1. Переводит в верхний регистр.
    2. Заменяет латинские символы на кириллические аналоги.
    """
    plate_upper = plate.upper()
    return "".join([CHAR_MAP.get(char, char) for char in plate_upper])

def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Вычисляет расстояние Левенштейна между двумя строками.
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def are_plates_similar(plate1: str, plate2: str, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """
    Сравнивает два номерных знака на схожесть с учетом культуры и порога совпадения.
    Возвращает True, если строки совпадают на 70% или более.
    """
    norm_plate1 = _normalize_plate(plate1)
    norm_plate2 = _normalize_plate(plate2)
    
    distance = _levenshtein_distance(norm_plate1, norm_plate2)
    max_len = max(len(norm_plate1), len(norm_plate2))
    
    if max_len == 0:
        return True # Оба номера пустые

    similarity = 1 - (distance / max_len)
    
    return similarity >= threshold 