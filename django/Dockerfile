# syntax=docker/dockerfile:1
FROM alpine:latest as builder
WORKDIR /code
RUN apk add --no-cache ffmpeg && \
    mkdir -p /code/libs && \
    cp $(ldd /usr/bin/ffmpeg | awk '/=>/ {print $3}') /code/libs/

# Pull base image
FROM python:3.12-alpine
# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /code

# Copy ffmpeg and required libraries from builder stage
COPY --from=builder /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=builder /code/libs/* /usr/lib/

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

