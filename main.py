import time
import re
import warnings

import cv2
import numpy as np
import torch

from colour_detection.detect_color import detect_color
from lpr_net.model.lpr_net import build_lprnet
from lpr_net.rec_plate import rec_plate, CHARS
from object_detection.detect_car_YOLO import ObjectDetection
from track_logic import check_numbers_overlaps
from detection_level import DetectionLevel

import settings
from database import SessionLocal
from services.car_passage_service import CarPassageService

# Игнорируем конкретное предупреждение от PyTorch
warnings.filterwarnings(
    "ignore",
    message="`torch.cuda.amp.autocast.*is deprecated"
)

def get_frames(video_src: str) -> np.ndarray:
    """
    Генератор, котрый читает видео и отдает фреймы
    """
    cap = cv2.VideoCapture(video_src)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            yield frame
        else:
            print("End video")
            break
    return None


def preprocess(image: np.ndarray, size: tuple) -> np.ndarray:
    """
    Препроцесс перед отправкой на YOLO
    Ресайз, нормализация и т.д.
    """
    image = cv2.resize(
        image, size, fx=0, fy=0, interpolation=cv2.INTER_CUBIC  # resolution
    )
    return image


def get_boxes(results, frame):

    """
    return dict with labels and cords
    :param results: inferences made by model
    :param frame: frame on which cords calculated
    :return: dict with labels and cords
    """

    labels, cord = results

    n = len(labels)
    x_shape, y_shape = frame.shape[1], frame.shape[0]

    labls_cords = {}
    numbers = []
    cars = []
    trucks = []
    buses = []

    for i in range(n):

        row = cord[i]
        x1, y1, x2, y2 = (
            int(row[0] * x_shape),
            int(row[1] * y_shape),
            int(row[2] * x_shape),
            int(row[3] * y_shape),
        )

        if labels[i] == 0:
            numbers.append((x1, y1, x2, y2))
        elif labels[i] == 1:
            cars.append((x1, y1, x2, y2))
        elif labels[i] == 2:
            trucks.append((x1, y1, x2, y2))
        elif labels[i] == 3:
            buses.append((x1, y1, x2, y2))

    labls_cords["numbers"] = numbers
    labls_cords["cars"] = cars
    labls_cords["trucks"] = trucks
    labls_cords["busses"] = buses

    return labls_cords


def plot_boxes(cars_list: list, frame: np.ndarray) -> np.ndarray:

    n = len(cars_list)

    for car in cars_list:

        car_type = car[2]
        has_plate = car[0] is not None

        # Get car coordinates and assign color based on vehicle type
        x1_car, y1_car, x2_car, y2_car = car[1][0] if isinstance(car[1], list) else car[1]
        
        # Set color based on vehicle type
        if car_type == "car":
            car_bgr = (0, 0, 255)  # Red
        elif car_type == "truck":
            car_bgr = (0, 255, 0)  # Green
        elif car_type == "bus":
            car_bgr = (255, 0, 0)  # Blue

        # Draw car box for all vehicles
        cv2.rectangle(frame, (x1_car, y1_car), (x2_car, y2_car), car_bgr, 2)
        
        # Display appropriate text for vehicle
        if has_plate:
            # Get plate coordinates and text
            x1_number, y1_number, x2_number, y2_number = car[0][0] if isinstance(car[0], list) else car[0]
            number = car[0][1] if isinstance(car[0], list) else "Unknown"
            
            # Get car color if available
            colour = car[1][1] if isinstance(car[1], list) else "unknown"
            
            # Draw vehicle info
            cv2.putText(
                frame,
                car_type + " " + colour,
                (x1_car, y2_car + 15),
                0,
                1,
                car_bgr,
                thickness=2,
                lineType=cv2.LINE_AA,
            )

            # Draw license plate box and text
            number_bgr = (255, 255, 255)  # White
            cv2.rectangle(
                frame, (x1_number, y1_number), (x2_number, y2_number), number_bgr, 2
            )
            cv2.putText(
                frame,
                number,
                (x1_number - 20, y2_number + 30),
                0,
                1,
                number_bgr,
                thickness=2,
                lineType=cv2.LINE_AA,
            )
        else:
            # Display text for vehicles without detected plates
            cv2.putText(
                frame,
                car_type + " (No plate)",
                (x1_car, y1_car - 10),
                0,
                0.7,
                car_bgr,
                thickness=2,
                lineType=cv2.LINE_AA,
            )

    detection_area = settings.DETECTION_AREA

    cv2.rectangle(frame, detection_area[0], detection_area[1], (0, 0, 0), 2)

    return frame


def check_roi(coords):
    """
    Check if object is within the detection area
    
    Args:
        coords: Bounding box coordinates (x1, y1, x2, y2)
    
    Returns:
        bool: True if object is in detection area
    """
    detection_area = settings.DETECTION_AREA

    # Calculate center point of the detection
    xc = int((coords[0] + coords[2]) / 2)
    yc = int((coords[1] + coords[3]) / 2)
    
    # Calculate box dimensions
    width = coords[2] - coords[0]
    height = coords[3] - coords[1]
    area = width * height
    
    # Center-based detection for all objects
    if (
        (detection_area[0][0] < xc < detection_area[1][0]) and 
        (detection_area[0][1] < yc < detection_area[1][1])
        ):
        return True
    
    # Size-adaptive handling
    if area < 10000:  # Small objects (distant vehicles)
        # More lenient - any overlap with detection area
        if (
            (coords[0] < detection_area[1][0] and coords[2] > detection_area[0][0]) and
            (coords[1] < detection_area[1][1] and coords[3] > detection_area[0][1])
        ):
            return True
    elif area > 50000:  # Large objects (close vehicles)
        # Stricter - at least 30% overlap with detection area
        x_overlap = min(coords[2], detection_area[1][0]) - max(coords[0], detection_area[0][0])
        y_overlap = min(coords[3], detection_area[1][1]) - max(coords[1], detection_area[0][1])
        
        if x_overlap > 0 and y_overlap > 0:
            overlap_area = x_overlap * y_overlap
            overlap_ratio = overlap_area / area
            if overlap_ratio > 0.3:
                return True
    
    return False


def main(
    video_file_path, 
    yolo_model_path,
    yolo_conf, 
    yolo_iou,
    lpr_model_path,
    lpr_max_len,
    lpr_dropout_rate, 
    device,
    detection_level=settings.DETECTION_LEVEL
    ):

    cv2.startWindowThread()
    
    # --- Database Connection ---
    db_session = SessionLocal()
    passage_service = CarPassageService(db_session)
    if not passage_service.test_connection():
        print("CRITICAL: Could not connect to the database. Exiting.")
        db_session.close()
        return
    # -------------------------

    detector = ObjectDetection(
        yolo_model_path, 
        conf=yolo_conf, 
        iou=yolo_iou,
        device = device
        )

    LPRnet = build_lprnet(
        lpr_max_len=lpr_max_len, 
        phase=False, 
        class_num=len(CHARS), 
        dropout_rate=lpr_dropout_rate
    )
    LPRnet.to(torch.device(device))
    LPRnet.load_state_dict(
        torch.load(lpr_model_path)
    )

    for raw_frame in get_frames(video_file_path):
        
        time_start = time.time()

        # Balanced resolution for both near and distant object detection (1024x768)
        proc_frame = preprocess(raw_frame, (1024, 768))
        results = detector.score_frame(proc_frame)
        labls_cords = get_boxes(results, raw_frame)
        
        # Use detection level to filter vehicles
        new_cars = check_numbers_overlaps(labls_cords, detection_level)

        # list to write cars that've been defined
        cars = []

        for car in new_cars:
            plate_coords = car[0]
            car_coords = car[1]

            # Process cars with detected plates
            if plate_coords is not None:
                if check_roi(plate_coords):
                    x1_car, y1_car = car_coords[0], car_coords[1]
                    x2_car, y2_car = car_coords[2], car_coords[3]

                    # define car's colour
                    car_box_image = raw_frame[y1_car:y2_car, x1_car:x2_car]
                    colour = detect_color(car_box_image)

                    car[1] = [car_coords, colour]

                    x1_plate, y1_plate = plate_coords[0], plate_coords[1]
                    x2_plate, y2_plate = plate_coords[2], plate_coords[3]

                    # define number on the plate
                    plate_box_image = raw_frame[y1_plate:y2_plate, x1_plate:x2_plate]
                    plate_text = rec_plate(LPRnet, plate_box_image)

                    # Skip if RECOGNIZED_PLATE level and no text was recognized
                    if detection_level == DetectionLevel.RECOGNIZED_PLATE and not plate_text:
                        continue

                    # check if number matches russian number type
                    if (
                        not re.match("[A-Z]{1}[0-9]{3}[A-Z]{2}[0-9]{2,3}", plate_text)
                        is None
                    ):
                        car[0] = [plate_coords, plate_text + "_RUSSIAN_PLATE"]
                        # --- Fixate Car Passage ---
                        result = passage_service.fixate_car_passage(plate_text)
                        print(f"INFO: Passage fixation for plate '{plate_text}': {result.name}")
                        # --------------------------
                    else:
                        car[0] = [plate_coords, plate_text + "_UNDEFINED"]


                    cars.append(car)
            # Process cars without plates (when detection_level is CAR_ONLY)
            elif detection_level == DetectionLevel.CAR_ONLY:
                x1_car, y1_car = car_coords[0], car_coords[1]
                x2_car, y2_car = car_coords[2], car_coords[3]
                
                # Check if car is in detection area
                if check_roi((x1_car, y1_car, x2_car, y2_car)):
                    # Define car's color
                    car_box_image = raw_frame[y1_car:y2_car, x1_car:x2_car]
                    colour = detect_color(car_box_image)
                    
                    car[1] = [car_coords, colour]
                    cars.append(car)

        drawn_frame = plot_boxes(cars, raw_frame)
        proc_frame = preprocess(drawn_frame, settings.FINAL_FRAME_RES)

        time_end = time.time()

        # print('time end: ',time_end)

        cv2.imshow("video", proc_frame)
        
        # wait 5 sec if push 's'
        if cv2.waitKey(30) & 0xFF == ord("s"):
            time.sleep(5)

        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    db_session.close()


if __name__ == "__main__":
    main(
        settings.FILE_PATH,
        settings.YOLO_MODEL_PATH,
        settings.YOLO_CONF, 
        settings.YOLO_IOU,
        settings.LPR_MODEL_PATH,
        settings.LPR_MAX_LEN, 
        settings.LPR_DROPOUT, 
        settings.DEVICE,
        settings.DETECTION_LEVEL
    )
