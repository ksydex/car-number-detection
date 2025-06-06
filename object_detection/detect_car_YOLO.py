import torch


class ObjectDetection:

    """
    The class performs generic object detection on a video file.
    It uses yolo5 pretrained model to make inferences and opencv2 to manage frames.
    Included Features:
    1. Reading and writing of video file using  Opencv2
    2. Using pretrained model to make inferences on frames.
    Upcoming Features:
    """

    def __init__(self, model_path, conf, iou, device):

        """
        :param input_file: provide youtube url which will act as input for the model.
        :param out_file: name of a existing file, or a new file in which to write the output.
        :return: void
        """
        self.__model_path = model_path
        self.model = self.load_model()

        # Basic detection parameters
        self.model.conf = conf
        self.model.iou = iou
        
        # Balanced settings for both near and distant object detection
        self.model.max_det = 50  # Moderate max detections to avoid too many false positives
        self.model.agnostic = True  # Class-agnostic NMS
        self.model.multi_label = False  # Single best label per box for cleaner detection
        
        # Enhanced parameters for balanced detection
        self.model.classes = None  # Detect all classes
        self.model.min_wh = 2  # Minimum width and height for detection (in pixels)
        self.model.max_wh = 7680  # Maximum width and height for detection
        
        self.device = device

    def load_model(self):

        """
        Function loads the yolo5 model from PyTorch Hub then use our custom weights.
        """

        model = torch.hub.load("ultralytics/yolov5", "custom", path=self.__model_path)
        return model

    def score_frame(self, frame):

        """
        function scores each frame of the video and returns results.
        :param frame: frame to be infered.
        :return: labels and coordinates of objects found.
        """
        self.model.to(self.device)
        
        # Set input image to original frame dimensions 
        # YOLOv5 has built-in letterboxing that handles multiple scales well
        frame_height, frame_width = frame.shape[:2]
        
        # Use a balanced inference size (1024) for both near and distant objects
        results = self.model([frame], size=1024)
        
        # Process all detections
        labels, cord = (
            results.xyxyn[0][:, -1].to("cpu").numpy(),
            results.xyxyn[0][:, :-1].to("cpu").numpy(),
        )
        return labels, cord
