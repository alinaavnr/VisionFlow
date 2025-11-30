"""Reusable image filter utilities for webcam frames."""
from __future__ import annotations

from typing import Callable, Dict

import cv2
import numpy as np

Frame = np.ndarray
FilterFunc = Callable[[Frame], Frame]


def apply_none(frame: Frame) -> Frame:
    return frame


def apply_gray(frame: Frame) -> Frame:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def apply_blur(frame: Frame, ksize: int = 11) -> Frame:
    k = ksize if ksize % 2 == 1 else ksize + 1
    return cv2.GaussianBlur(frame, (k, k), 0)


def apply_edges(frame: Frame, low_threshold: int = 50, high_threshold: int = 150) -> Frame:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, low_threshold, high_threshold)


FILTERS: Dict[str, FilterFunc] = {
    "Оригинал": apply_none,
    "Оттенки серого": apply_gray,
    "Размытие": apply_blur,
    "Грани": apply_edges,
}

