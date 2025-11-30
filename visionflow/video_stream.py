"""Video stream abstraction around OpenCV capture."""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

from .filters import FILTERS, FilterFunc


class VideoStream:
    def __init__(
        self,
        camera_index: int = 0,
        filter_name: str = "Оригинал",
        snapshot_dir: Union[Path, str] = Path("snapshots"),
    ) -> None:
        self.camera_index = camera_index
        self.filter_name = filter_name
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self._capture: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._frame_lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._processed_frame: Optional[np.ndarray] = None
        self._frame_count = 0
        self._fps = 0.0
        self._last_time = None

    @property
    def frame(self) -> Optional[np.ndarray]:
        with self._frame_lock:
            return None if self._processed_frame is None else self._processed_frame.copy()

    @property
    def frame_info(self) -> str:
        with self._frame_lock:
            if self._frame is None:
                return "Нет данных"
            height, width = self._frame.shape[:2]
            return f"Кадр: {width}x{height}, FPS: {self._fps:.1f}, Всего кадров: {self._frame_count}"

    def set_filter(self, name: str) -> None:
        if name not in FILTERS:
            raise ValueError(f"Неизвестный фильтр: {name}")
        self.filter_name = name

    def start(self) -> None:
        if self._running.is_set():
            return
        self._capture = cv2.VideoCapture(self.camera_index)
        if not self._capture.isOpened():
            raise RuntimeError("Не удалось открыть веб-камеру")
        self._running.set()
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
        if self._capture:
            self._capture.release()
            self._capture = None

    def snapshot(self) -> Path:
        frame = self.frame
        if frame is None:
            raise RuntimeError("Нет кадра для сохранения")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = self.snapshot_dir / f"snapshot_{timestamp}.png"
        cv2.imwrite(str(path), frame)
        return path

    def _update_loop(self) -> None:
        self._last_time = time.time()
        while self._running.is_set():
            if not self._capture:
                break
            ret, frame = self._capture.read()
            if not ret:
                continue
            self._frame_count += 1
            now = time.time()
            dt = now - self._last_time if self._last_time else 0
            if dt > 0:
                self._fps = 1.0 / dt
            self._last_time = now

            filter_func: FilterFunc = FILTERS.get(self.filter_name, FILTERS["Оригинал"])
            processed = filter_func(frame)
            if processed.ndim == 2:
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)

            with self._frame_lock:
                self._frame = frame
                self._processed_frame = processed

        self._running.clear()

    def __enter__(self) -> "VideoStream":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()
