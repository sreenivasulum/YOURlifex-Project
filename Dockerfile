FROM python:3.11.0

# Install dependencies necessary to build and run FFmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    yasm \
    git \
    curl \
    portaudio19-dev \
    libffi-dev \
    libssl-dev \
    libx264-dev \
    libopus-dev

RUN echo "deb http://deb.debian.org/debian/ bullseye main\ndeb-src http://deb.debian.org/debian/ bullseye main" | tee /etc/apt/sources.list.d/ffmpeg.list  &&\
    apt-get update && \
    apt-get install -y ffmpeg=7:4.3.6-0+deb11u1


ENV PYTHONUNBUFFERED 1

WORKDIR /lifex_users_api

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

ARG DEV=false
RUN if [ "$DEV" = "true" ] ; then poetry install --with dev ; else poetry install --only main ; fi

COPY ./lifex_users_api/ ./

ENV PYTHONPATH "${PYTHONPATH}:/lifex_users_api"
ENV PORT 8080

EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
