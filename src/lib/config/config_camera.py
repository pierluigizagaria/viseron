import logging
import os

from const import (
    CAMERA_GLOBAL_ARGS,
    CAMERA_HWACCEL_ARGS,
    CAMERA_INPUT_ARGS,
    CAMERA_OUTPUT_ARGS,
    ENV_CUDA_SUPPORTED,
    ENV_OPENCL_SUPPORTED,
    ENV_RASPBERRYPI3,
    HWACCEL_CUDA_DECODER,
    HWACCEL_OPENCL_DECODER,
    HWACCEL_RPI3_DECODER,
)
from lib.helpers import slugify
from voluptuous import All, Any, Length, Optional, Range, Required, Schema

LOGGER = logging.getLogger(__name__)


def ensure_mqtt_name(camera_data: list) -> list:
    for camera in camera_data:
        if camera["mqtt_name"] is None:
            camera["mqtt_name"] = slugify(camera["name"])
    return camera_data


def check_for_hwaccels(hwaccel_args: list) -> list:
    if hwaccel_args:
        return hwaccel_args

    if os.getenv(ENV_CUDA_SUPPORTED) == "true":
        return HWACCEL_CUDA_DECODER
    if os.getenv(ENV_OPENCL_SUPPORTED) == "true":
        return HWACCEL_OPENCL_DECODER
    if os.getenv(ENV_RASPBERRYPI3) == "true":
        return HWACCEL_RPI3_DECODER
    return hwaccel_args


SCHEMA = Schema(
    All(
        [
            {
                Required("name"): All(str, Length(min=1)),
                Optional("mqtt_name", default=None): Any(All(str, Length(min=1)), None),
                Required("host"): All(str, Length(min=1)),
                Required("port"): All(int, Range(min=1)),
                Optional("username", default=None): Any(All(str, Length(min=1)), None),
                Optional("password", default=None): Any(All(str, Length(min=1)), None),
                Required("path"): All(str, Length(min=1)),
                Optional("width", default=None): Any(int, None),
                Optional("height", default=None): Any(int, None),
                Optional("fps", default=None): Any(All(int, Range(min=1)), None),
                Optional("global_args", default=CAMERA_GLOBAL_ARGS): list,
                Optional("input_args", default=CAMERA_INPUT_ARGS): list,
                Optional(
                    "hwaccel_args", default=CAMERA_HWACCEL_ARGS
                ): check_for_hwaccels,
                Optional("filter_args", default=[]): list,
            }
        ],
        ensure_mqtt_name,
    )
)


class CameraConfig:
    schema = SCHEMA

    def __init__(self, camera):
        self._name = camera.name
        self._mqtt_name = camera.mqtt_name
        self._host = camera.host
        self._port = camera.port
        self._username = camera.username
        self._password = camera.password
        self._path = camera.path
        self._width = camera.width
        self._height = camera.height
        self._fps = camera.fps
        self._global_args = camera.global_args
        self._input_args = camera.input_args
        self._hwaccel_args = camera.hwaccel_args
        self._filter_args = camera.filter_args

    @property
    def name(self):
        return self._name

    @property
    def mqtt_name(self):
        return self._mqtt_name

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def path(self):
        return self._path

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def fps(self):
        return self._fps

    @property
    def stream_url(self):
        return (
            f"rtsp://{self.username}:{self.password}@{self.host}:{self.port}{self.path}"
        )

    @property
    def global_args(self):
        return self._global_args

    @property
    def input_args(self):
        return self._input_args

    @property
    def hwaccel_args(self):
        return self._hwaccel_args

    @property
    def filter_args(self):
        return self._filter_args

    @property
    def output_args(self):
        return CAMERA_OUTPUT_ARGS
