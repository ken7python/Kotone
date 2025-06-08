from idlelib.configdialog import changes

import sounddevice as sd
from pydub.effects import normalize
import noisereduce as nr
import librosa
import soundfile as sf
from scipy.io.wavfile import write
from pydub import AudioSegment
import os
import numpy as np

fs = 44100
channels = 1
seconds = 5
recording = []

print("録音開始...(Enterキーで停止)")
sd.default.samplerate = fs
sd.default.channels = channels

def callback(indata, frames, time, status):
    recording.append(indata.copy())

stream = sd.InputStream(callback=callback)
stream.start()

input()
stream.stop()
stream.close()

audio_np = np.concatenate(recording, axis=0)
write('temp.wav', fs, audio_np)
print("録音完了。")
audio = AudioSegment.from_wav('temp.wav')

print('ノーマライズ中...')
normalized = normalize(audio)
normalized.export('normalized.mp3',format="mp3")

print('ノイズ除去...')
y, sr = librosa.load("normalized.mp3", sr=None)
reduced = nr.reduce_noise(y=y, sr=sr)
sf.write('output.mp3', reduced, fs)