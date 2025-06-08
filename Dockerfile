FROM python:3.11-slim

# Установка зависимостей для pygame и X11
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libx11-6 \
        x11-apps \
        && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . /app
WORKDIR /app

# Указываем переменную окружения для X11
ENV DISPLAY=${DISPLAY}

# Точка входа
CMD ["python", "gui.py"]
