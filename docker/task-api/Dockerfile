FROM python:3.9.6-slim-bullseye as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG PYTHON_VENV=/opt/.venv
ARG SERVICE_WORKDIR=/opt/app
ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}

RUN apt-get update \
     && apt-get install -y netcat-traditional gettext libpq-dev python-dev

RUN groupadd --gid ${GID} user \
      && useradd --uid ${UID} --gid user --shell /bin/bash --create-home user

COPY ./src/requirements.txt .

RUN python -m venv "${PYTHON_VENV}" \
    && "${PYTHON_VENV}/bin/python" -m pip install --no-cache-dir --upgrade pip \
    && "${PYTHON_VENV}/bin/pip" install --no-cache-dir -r /requirements.txt

ENV PATH="${PYTHON_VENV}/bin:${PATH}"

WORKDIR "${SERVICE_WORKDIR}"

COPY ./src/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT  [ "/entrypoint.sh" ]

EXPOSE 8000
USER user

# Local stage
FROM base as local

# Server stage
FROM base as server
COPY ./src/. .
