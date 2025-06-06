import os
import torch
from detection_level import DetectionLevel

DEVICE = 'cuda'# 'cuda' if torch.cuda.is_available() else 'cpu'

FILE_PATH = os.environ.get(
    'file_path', 
    os.path.normpath("test/videos/test.mp4")
)
YOLO_MODEL_PATH = os.environ.get(
    'yolo_model', 
    os.path.normpath("object_detection/YOLOS_cars.pt")
)
LPR_MODEL_PATH = os.environ.get(
    'lpr_model', 
    os.path.normpath("lpr_net/model/weights/LPRNet__iteration_2000_28.09.pth")
)

# Balanced confidence threshold for both near and distant objects
YOLO_CONF = 0.4
# Lower IoU threshold for better overlap handling
YOLO_IOU = 0.3
LPR_MAX_LEN = 9
LPR_DROPOUT = 0

# Higher resolution for better detection while still handling close objects
FINAL_FRAME_RES = (1280, 720)
# Full frame detection area (assuming 1920x1080 video)
DETECTION_AREA = [(0, 0), (1920, 1080)]

# Default detection level - only render vehicles with license plates
DETECTION_LEVEL = DetectionLevel.LICENSE_PLATE

DATABASE_URL = 'postgresql://root:root@localhost:5432/car_vision'
WITHDRAWAL_AMOUNT = 500
