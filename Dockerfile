FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv
RUN uv sync --no-dev

COPY src ./src

CMD ["uv", "run", "streamlit", "run", "src/main.py"]