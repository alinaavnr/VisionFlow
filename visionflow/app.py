"""Tkinter-based GUI application for webcam streaming."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import Optional

import cv2
from PIL import Image, ImageTk

from .filters import FILTERS
from .video_stream import VideoStream


class VisionFlowApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("VisionFlow — обработка видеопотока")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        self.filter_var = tk.StringVar(value=list(FILTERS.keys())[0])
        self.info_var = tk.StringVar(value="Кадр: нет данных")

        self.video_stream = VideoStream()
        self._image_ref: Optional[ImageTk.PhotoImage] = None
        self._update_job: Optional[str] = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        self.video_label = ttk.Label(main, text="Нажмите Старт для запуска", anchor="center", background="#1f1f1f", foreground="#f0f0f0")
        self.video_label.pack(fill="both", expand=True, pady=(0, 10))

        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=5)

        self.start_btn = ttk.Button(controls, text="Старт", command=self.start_stream)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(controls, text="Стоп", command=self.stop_stream)
        self.stop_btn.grid(row=0, column=1, padx=5)

        ttk.Label(controls, text="Фильтр:").grid(row=0, column=2, padx=(15, 5))
        filter_box = ttk.Combobox(controls, textvariable=self.filter_var, state="readonly", values=list(FILTERS.keys()), width=18)
        filter_box.grid(row=0, column=3, padx=5)
        filter_box.bind("<<ComboboxSelected>>", lambda _: self.on_filter_change())

        snapshot_btn = ttk.Button(controls, text="Захватить изображение", command=self.take_snapshot)
        snapshot_btn.grid(row=0, column=4, padx=(15, 0))

        controls.columnconfigure(3, weight=1)

        info_frame = ttk.Frame(main)
        info_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(info_frame, textvariable=self.info_var, anchor="w").pack(fill="x")

    def start_stream(self) -> None:
        try:
            self.video_stream.start()
            self._ensure_updates()
            self.start_btn.state(["disabled"])
            self.stop_btn.state(["!disabled"])
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", str(exc))

    def stop_stream(self) -> None:
        self.video_stream.stop()
        if self._update_job:
            self.root.after_cancel(self._update_job)
            self._update_job = None
        self.start_btn.state(["!disabled"])
        self.stop_btn.state(["disabled"])

    def on_filter_change(self) -> None:
        try:
            self.video_stream.set_filter(self.filter_var.get())
        except ValueError as exc:
            messagebox.showerror("Ошибка фильтра", str(exc))

    def take_snapshot(self) -> None:
        try:
            path = self.video_stream.snapshot()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Не удалось сохранить", str(exc))
            return
        messagebox.showinfo("Снимок сохранён", f"Файл: {path}")

    def _ensure_updates(self) -> None:
        if self._update_job is None:
            self._update_frame()

    def _update_frame(self) -> None:
        frame = self.video_stream.frame
        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb)
            self._image_ref = ImageTk.PhotoImage(image=image)
            self.video_label.configure(image=self._image_ref, text="")  # type: ignore[arg-type]
        else:
            self.video_label.configure(text="Ожидание данных")
        self.info_var.set(self.video_stream.frame_info)
        self._update_job = self.root.after(33, self._update_frame)  # type: ignore[arg-type]

    def on_close(self) -> None:
        self.stop_stream()
        self.root.destroy()


def run_app() -> None:
    root = tk.Tk()
    app = VisionFlowApp(root)
    app.stop_btn.state(["disabled"])  # Стрим еще не идёт
    root.mainloop()


__all__ = ["run_app", "VisionFlowApp"]
