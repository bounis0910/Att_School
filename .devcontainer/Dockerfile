# ---------- build arguments ----------
ARG PYTHON_VERSION=3.11

# ---------- base image ----------
FROM python:${PYTHON_VERSION}-slim

# ---------- environment variables ----------
ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# ---------- system dependencies ----------
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- install Poetry ----------
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

# ---------- working directory ----------
WORKDIR /att_school

# ---------- copy dependency files ----------
COPY pyproject.toml poetry.lock* ./

# ---------- install python dependencies ----------
RUN poetry install --no-root

# ---------- copy application ----------
COPY . .

# ---------- default command ----------
CMD ["python", "app.py"]
