FROM python:3.10

RUN apt update && apt install -y ffmpeg wget unzip

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip \
 && unzip vosk-model-small-en-us-0.15.zip \
 && mv vosk-model-small-en-us-0.15 model

CMD ["python","app.py"]
