FROM python:3.6


ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /src

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt