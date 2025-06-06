from enum import Enum, auto

class DetectionLevel(Enum):
    """
    Controls which level of detection should be rendered in the visualization
    """
    # Render all detected vehicles regardless of license plate detection
    CAR_ONLY = auto()
    
    # Only render vehicles with detected license plates (default)
    LICENSE_PLATE = auto()
    
    # Only render vehicles with successfully recognized license plates
    RECOGNIZED_PLATE = auto() 