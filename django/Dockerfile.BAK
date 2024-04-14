# syntax=docker/dockerfile:1
FROM alpine:latest as builder
WORKDIR /code
RUN apk add --no-cache ffmpeg



# Pull base image
FROM python:3.12-alpine
# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /code
COPY --from=builder /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=builder /usr/lib/* /usr/lib/
#COPY --from=builder /root/vlmcsd/etc/vlmcsd.kmd /vlmcsd.kmd
# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# COPY ./uget_to_get.txt /usr/local/lib/python3.11/site-packages/snowpenguin/django/recaptcha3/fields.py

# Copy project
#COPY . .
# EXPOSE 8000

# ENTRYPOINT ["python", "manage.py", "runserver"]
# CMD ["0.0.0.0:8000"]

