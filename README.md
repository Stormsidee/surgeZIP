# SurgeZIP

Настольный архиватор на Python и PyQt5. Показывает содержимое архивов, позволяет выбрать файлы для извлечения и поддерживает drag-and-drop.

## Запуск из исходников

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Проект ориентирован на Windows. Поддержка RAR, 7Z и ISO зависит от соответствующих библиотек и утилит.

`main.py` содержит главное окно, `module/` содержит вспомогательные компоненты интерфейса и интеграцию с Windows. `build.py` и файлы PyInstaller используются для локальной сборки.
