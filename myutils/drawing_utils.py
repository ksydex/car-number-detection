from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from services.fixation_result import FixationResult
from services.passage_enums import PassageResult
from entities.user import User

def generate_log_message(result: FixationResult, plate_text: str) -> Optional[str]:
    """
    Формирует лог-сообщение на основе результата фиксации.
    """
    status = result.status
    user = result.user

    if status in [PassageResult.ALREADY_PROCESSED_IN_SESSION, PassageResult.CAR_NOT_FOUND]:
        return None  # Не логгируем эти события

    fio = "Неизвестный"
    if user:
        fio = f"{user.last_name} {user.first_name[0]}."
        if user.patronymic:
            fio += f"{user.patronymic[0]}."

    if status == PassageResult.ARRIVAL:
        return f"Владелец: {fio}. Зафиксирован въезд."
    elif status == PassageResult.DEPARTURE_WITH_MONEY_WITHDRAW:
        return f"Владелец: {fio}. Выезд с оплатой."
    elif status == PassageResult.DEPARTURE_USER_NO_MONEY:
        return f"Владелец: {fio}. Выезд (нет средств)."
    
    return None


def draw_log_panel(frame: np.ndarray, logs: list, max_logs: int = 5):
    """
    Отрисовывает панель с последними сообщениями лога в правом верхнем углу кадра.
    Использует Pillow для корректного отображения кириллицы.
    """
    if not logs:
        return frame
        
    font_size = 22
    font_path = "C:/Windows/Fonts/arial.ttf" # Стандартный путь для Windows.
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default() # Запасной вариант, если шрифт не найден

    # Отображаем только последние N сообщений
    display_logs = logs[-max_logs:]

    # Конвертируем кадр OpenCV в изображение Pillow
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil, 'RGBA')

    # Определяем ширину и высоту панели
    line_height = font_size + 10
    panel_height = len(display_logs) * line_height + 10
    
    max_text_width = 0
    for log in display_logs:
        text_width = draw.textlength(log, font=font)
        if text_width > max_text_width:
            max_text_width = int(text_width)
            
    # Координаты панели
    panel_x1 = img_pil.width - max_text_width - 40
    panel_y1 = 20
    panel_x2 = img_pil.width - 20
    panel_y2 = panel_y1 + panel_height

    # Отрисовка полупрозрачного фона
    draw.rectangle([(panel_x1, panel_y1), (panel_x2, panel_y2)], fill=(0, 0, 0, 128))

    # Отрисовка текста
    for i, log in enumerate(display_logs):
        text_y = panel_y1 + 5 + i * line_height
        draw.text((panel_x1 + 10, text_y), log, font=font, fill=(255, 255, 255, 255))
        
    # Конвертируем обратно в кадр OpenCV
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR) 