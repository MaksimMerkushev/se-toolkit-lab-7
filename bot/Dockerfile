FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen

# Копируем остальной код бота
COPY . .

# Запускаем бота через uv
CMD ["uv", "run", "bot.py"]
# Task 2 done
# Workflow verification for Task 4
