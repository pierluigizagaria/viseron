"""Face recognition module."""
from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from threading import Timer
from typing import Any
from uuid import uuid4

import cv2
import voluptuous as vol

from viseron.domains.post_processor import BASE_CONFIG_SCHEMA, AbstractPostProcessor
from viseron.helpers import create_directory
from viseron.helpers.schemas import FLOAT_MIN_ZERO

from .binary_sensor import FaceDetectionBinarySensor
from .const import (
    CONFIG_DETECT_REMOTE_FACES,
    CONFIG_EXPIRE_AFTER,
    CONFIG_FACE_RECOGNITION_PATH,
    CONFIG_SAVE_UNKNOWN_FACES,
    CONFIG_UNKNOWN_FACES_PATH,
    DEFAULT_DETECT_REMOTE_FACES,
    DEFAULT_EXPIRE_AFTER,
    DEFAULT_FACE_RECOGNITION_PATH,
    DEFAULT_SAVE_UNKNOWN_FACES,
    DEFAULT_UNKNOWN_FACES_PATH,
    DESC_DETECT_REMOTE_FACES,
    DESC_EXPIRE_AFTER,
    DESC_FACE_RECOGNITION_PATH,
    DESC_SAVE_UNKNOWN_FACES,
    DESC_UNKNOWN_FACES_PATH,
    EVENT_FACE_DETECTED,
    EVENT_FACE_EXPIRED,
)

BASE_CONFIG_SCHEMA = BASE_CONFIG_SCHEMA.extend(
    {
        vol.Optional(
            CONFIG_FACE_RECOGNITION_PATH,
            default=DEFAULT_FACE_RECOGNITION_PATH,
            description=DESC_FACE_RECOGNITION_PATH,
        ): str,
        vol.Optional(
            CONFIG_SAVE_UNKNOWN_FACES,
            default=DEFAULT_SAVE_UNKNOWN_FACES,
            description=DESC_SAVE_UNKNOWN_FACES,
        ): bool,
        vol.Optional(
            CONFIG_UNKNOWN_FACES_PATH,
            default=DEFAULT_UNKNOWN_FACES_PATH,
            description=DESC_UNKNOWN_FACES_PATH,
        ): str,
        vol.Optional(
            CONFIG_EXPIRE_AFTER,
            default=DEFAULT_EXPIRE_AFTER,
            description=DESC_EXPIRE_AFTER,
        ): FLOAT_MIN_ZERO,
        vol.Optional(
            CONFIG_DETECT_REMOTE_FACES,
            default=DEFAULT_DETECT_REMOTE_FACES,
            description=DESC_DETECT_REMOTE_FACES,
        ): bool,
    }
)


@dataclass
class FaceDict:
    """Representation of a face."""

    name: str
    coordinates: tuple[int, int, int, int]
    confidence: float | None
    timer: Timer
    extra_attributes: None | dict[str, Any] = None


@dataclass
class EventFaceDetected:
    """Hold information on face detection event."""

    camera_identifier: str
    face: FaceDict


class AbstractFaceRecognition(AbstractPostProcessor):
    """Abstract face recognition."""

    def __init__(self, vis, component, config, camera_identifier) -> None:
        super().__init__(vis, config, camera_identifier)
        self._faces: dict[str, FaceDict] = {}
        if config[CONFIG_SAVE_UNKNOWN_FACES]:
            create_directory(config[CONFIG_UNKNOWN_FACES_PATH])

        if os.path.isdir(config[CONFIG_FACE_RECOGNITION_PATH]):
            for face_dir in os.listdir(config[CONFIG_FACE_RECOGNITION_PATH]):
                if face_dir == "unknown":
                    continue
                vis.add_entity(
                    component, FaceDetectionBinarySensor(vis, self._camera, face_dir)
                )

    def known_face_found(
        self,
        component: str,
        face: str,
        coordinates: tuple[int, int, int, int],
        confidence=None,
        extra_attributes=None,
    ) -> None:
        """Adds/expires known faces."""
        # Cancel the expiry timer if face has already been detected
        if self._faces.get(face, None):
            self._faces[face].timer.cancel()

        if self._config[CONFIG_DETECT_REMOTE_FACES] and not self._faces.get(face, None):
            self._vis.add_entity(
                component, FaceDetectionBinarySensor(self._vis, self._camera, face)
            )

        # Adds a detected face and schedules an expiry timer
        face_dict = FaceDict(
            face,
            coordinates,
            confidence,
            Timer(self._config[CONFIG_EXPIRE_AFTER], self.expire_face, [face]),
            extra_attributes=extra_attributes,
        )
        face_dict.timer.start()

        self._vis.dispatch_event(
            EVENT_FACE_DETECTED.format(
                camera_identifier=self._camera.identifier, face=face
            ),
            EventFaceDetected(
                camera_identifier=self._camera.identifier,
                face=face_dict,
            ),
        )
        self._faces[face] = face_dict

    def unknown_face_found(self, component: str, frame) -> None:
        """Save unknown faces."""
        unique_id = (
            f"{datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S-')}"
            f"{component}-{str(uuid4())}.jpg"
        )
        file_name = os.path.join(self._config[CONFIG_UNKNOWN_FACES_PATH], unique_id)
        self._logger.debug(f"Unknown face found, saving to {file_name}")

        if not cv2.imwrite(file_name, frame):
            self._logger.error("Failed saving unknown face image to disk")

    def expire_face(self, face) -> None:
        """Expire no longer found face."""
        self._logger.debug(f"Expiring face {face}")
        self._vis.dispatch_event(
            EVENT_FACE_EXPIRED.format(
                camera_identifier=self._camera.identifier, face=face
            ),
            EventFaceDetected(
                camera_identifier=self._camera.identifier,
                face=self._faces[face],
            ),
        )
