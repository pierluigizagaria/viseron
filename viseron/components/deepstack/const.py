"""DeepStack constants."""

COMPONENT = "deepstack"


# CONFIG_SCHEMA constants
CONFIG_OBJECT_DETECTOR = "object_detector"
CONFIG_FACE_RECOGNITION = "face_recognition"
CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_API_KEY = "api_key"
CONFIG_TIMEOUT = "timeout"

DEFAULT_API_KEY = None
DEFAULT_TIMEOUT = 10


# OBJECT_DETECTOR_SCHEMA constants
CONFIG_IMAGE_WIDTH = "image_width"
CONFIG_IMAGE_HEIGHT = "image_height"
CONFIG_CUSTOM_MODEL = "custom_model"

DEFAULT_IMAGE_WIDTH = None
DEFAULT_IMAGE_HEIGHT = None
DEFAULT_CUSTOM_MODEL = None


# FACE_RECOGNITION_SCHEMA constants
CONFIG_TRAIN = "train"
CONFIG_MIN_CONFIDENCE = "min_confidence"

DEFAULT_TRAIN = True
DEFAULT_MIN_CONFIDENCE = 0.8
