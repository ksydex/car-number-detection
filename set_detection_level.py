import settings
from detection_level import DetectionLevel

def set_detection_level(level):
    """
    Set the global detection level that controls what is rendered
    
    Args:
        level: DetectionLevel enum value (CAR_ONLY, LICENSE_PLATE, RECOGNIZED_PLATE)
        
    Example:
        from set_detection_level import set_detection_level
        from detection_level import DetectionLevel
        
        # To show all cars regardless of plate detection:
        set_detection_level(DetectionLevel.CAR_ONLY)
        
        # To show only cars with recognized plates:
        set_detection_level(DetectionLevel.RECOGNIZED_PLATE)
        
        # To reset to default (show cars with detected plates):
        set_detection_level(DetectionLevel.LICENSE_PLATE)
    """
    if not isinstance(level, DetectionLevel):
        raise ValueError(f"Level must be a DetectionLevel enum value, got {type(level)}")
    
    settings.DETECTION_LEVEL = level
    print(f"Detection level set to: {level.name}")
    return level 