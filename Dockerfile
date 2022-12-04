FROM python:3.9

ARG UID=1000 \
  GID=1000

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.2.1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /code

RUN groupadd -g "${GID}" -r user \
  && useradd -d '/code' -g user -l -r -u "${UID}" user \
  && chown user:user -R '/code' 

COPY --chown=user:user ./src/ /code/src/

COPY --chown=user:user ./poetry.lock ./pyproject.toml ./.env /code/

RUN poetry install --only main --no-interaction --no-ansi

COPY ./cron/daily_updater /etc/cron.d/

USER user

CMD ["gunicorn", "src.app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", ":8000", "--log-file", "-"]