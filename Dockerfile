# ─────────────────────────────────────────────────────────────────────────────
#  Config Inspector — Dockerfile
#  GUI-приложение на PyQt6, требует X11-дисплей.
#
#  Варианты запуска:
#    1. Linux-хост c X11 (самый простой):
#       docker build -t config-inspector .
#       docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix config-inspector
#
#    2. Headless (тест/CI) через Xvfb:
#       docker run --rm config-inspector xvfb-run -a python main.py
#
#    3. Windows/macOS через VNC (docker-compose.yml):
#       docker compose up
#       → открой браузер: http://localhost:6080
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# ── Метаданные ─────────────────────────────────────────────────────────────────
LABEL maintainer="Efros Config Inspector Team"
LABEL description="Config Inspector — система мониторинга целостности устройств"
LABEL version="1.0.0"

# ── Системные зависимости Qt6 и X11 ───────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt6 runtime libs
    libgl1-mesa-glx \
    libglib2.0-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-util1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    # EGL / OpenGL
    libegl1 \
    libgles2 \
    # Виртуальный дисплей для headless-режима
    xvfb \
    x11-xserver-utils \
    # Шрифты (кириллица)
    fonts-dejavu-core \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Рабочая директория ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python-зависимости (сначала requirements — кэшируемый слой) ────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Исходный код ───────────────────────────────────────────────────────────────
COPY . .

# ── Переменные окружения для Qt ───────────────────────────────────────────────
ENV QT_QPA_PLATFORM=xcb
ENV QT_XCB_GL_INTEGRATION=none
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── Порт (не нужен для desktop-GUI, оставлен для VNC-образа) ──────────────────
EXPOSE 5900
EXPOSE 6080

# ── Точка входа: запуск через виртуальный дисплей ─────────────────────────────
# При наличии реального $DISPLAY (X11-forwarding) Xvfb не нужен —
# просто переопределите CMD: docker run ... python main.py
CMD ["xvfb-run", "-a", "--server-args=-screen 0 1280x800x24", "python", "main.py"]
