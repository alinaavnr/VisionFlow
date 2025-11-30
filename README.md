# VisionFlow

Приложение для потоковой обработки видео с веб-камеры на Python (Tkinter + OpenCV).

## Возможности
- Графический интерфейс на Tkinter с управлением старт/стоп.
- Выбор фильтров (оригинал, оттенки серого, размытие, грани).
- Сохранение снимков (`snapshots/`).
- Информация о кадре: размер, FPS, число кадров.

## Стек
- **Стандартные библиотеки:** `tkinter`, `pathlib`, `threading`, `time` и т. д.
- **Популярные библиотеки:** `opencv-python`, `Pillow`, `numpy`.

## Установка
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск
```bash
python main.py
```

## Тесты
```bash
python -m pytest
```
