FROM python:3.8

EXPOSE 5000


RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD [ "flask", "run", "--host", "0.0.0.0"]

