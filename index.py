from idlelib.configdialog import changes

import sounddevice as sd
from pydub.effects import normalize,compress_dynamic_range

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

output_dir = './outputs'
filename = str(input('Enter filename:'))
if filename == '':
    filename = 'output.mp3'
else:
    root, ext = os.path.splitext(filename)
    if ext == '':
        filename += '.mp3'


print("Start Recording...(Press Enter to stop)")
sd.default.samplerate = fs
sd.default.channels = channels

def callback(indata, frames, time, status):
    recording.append(indata.copy())

stream = sd.InputStream(callback=callback)
stream.start()

input()
stream.stop()
stream.close()

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

audio_np = np.concatenate(recording, axis=0)
write(f'{output_dir}/temp.wav', fs, audio_np)
print("Finished Recording.")
audio = AudioSegment.from_wav(f'{output_dir}/temp.wav')

print('Normalizing...')
normalized = normalize(audio)
normalized.export(f'{output_dir}/normalized.wav',format="mp3")

print('Compresing ...')
compressed = compress_dynamic_range(normalized)
compressed.export(f'{output_dir}/compressed.wav',format="wav")

print('Noise Reduced...')
y, sr = librosa.load(f'{output_dir}/compressed.wav', sr=None)
reduced = nr.reduce_noise(y=y, sr=sr)
sf.write(f'{output_dir}/{filename}', reduced, fs)

#os.remove(f'{output_dir}/temp.wav')
#os.remove(f'{output_dir}/normalized.wav')
#os.remove(f'{output_dir}/compressed.wav')