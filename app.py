from flask import Flask, request, send_file, jsonify
import subprocess
import uuid
import requests
import os
from vosk import Model, KaldiRecognizer
import wave
import json
from gtts import gTTS

app = Flask(__name__)

model = Model("model")

def download_video(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

def extract_audio(video, audio):
    subprocess.run([
        "ffmpeg","-y",
        "-i", video,
        "-vn",
        "-acodec","pcm_s16le",
        "-ar","16000",
        "-ac","1",
        audio
    ])

def speech_to_text(audio):
    wf = wave.open(audio,"rb")
    rec = KaldiRecognizer(model,wf.getframerate())

    text=""

    while True:
        data=wf.readframes(4000)
        if len(data)==0:
            break
        if rec.AcceptWaveform(data):
            result=json.loads(rec.Result())
            text+=result.get("text"," ")

    return text

def translate(text):
    from googletrans import Translator
    translator=Translator()
    result=translator.translate(text,dest="am")
    return result.text

def tts_amharic(text,audio):
    tts=gTTS(text,lang="am")
    tts.save(audio)

def merge(video,audio,out):
    subprocess.run([
        "ffmpeg","-y",
        "-i",video,
        "-i",audio,
        "-c:v","copy",
        "-map","0:v:0",
        "-map","1:a:0",
        out
    ])

@app.route("/translate-video",methods=["POST"])
def translate_video():

    data=request.json
    url=data["video_url"]

    uid=str(uuid.uuid4())

    video=f"{uid}.mp4"
    audio=f"{uid}.wav"
    voice=f"{uid}_am.mp3"
    output=f"{uid}_final.mp4"

    download_video(url,video)

    extract_audio(video,audio)

    text=speech_to_text(audio)

    amharic=translate(text)

    tts_amharic(amharic,voice)

    merge(video,voice,output)

    return send_file(output,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
