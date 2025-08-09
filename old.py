import datetime
import os

import librosa
import noisereduce as nr
import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize
from scipy.io.wavfile import write

fs = 44100
channels = 1

output_dir = f"./outputs/{datetime.datetime.now().strftime('%Y-%m-%d')}"

print("----------------")
while True:
    recording = []
    filename = str(input("Enter filename:"))
    if filename == "":
        filename = "output.mp3"
    else:
        root, ext = os.path.splitext(filename)
        if ext == "":
            filename += ".mp3"

    print("----------------")

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
    write(f"{output_dir}/temp.wav", fs, audio_np)
    print("Export Recording.")

    print("Noise Reduced...")
    y, sr = librosa.load(f"{output_dir}/temp.wav", sr=None)
    reduced = nr.reduce_noise(y=y, sr=sr)
    sf.write(f"{output_dir}/noise_reduced.wav", reduced, fs)

    audio = AudioSegment.from_wav(f"{output_dir}/noise_reduced.wav")

    print("Normalizing...")
    normalized = normalize(audio)
    normalized.export(f"{output_dir}/normalized.wav", format="mp3")

    print("Compresing ...")
    compressed = compress_dynamic_range(
        normalized,
        threshold=-30.0,  # 小さい音まで拾う
        ratio=6.0,  # 強めの圧縮（通常は2〜4）
        attack=5,  # 反応スピード（ms）
        release=50,  # 落ち着きに戻る時間（ms）
    )
    compressed.export(f"{output_dir}/compressed.wav", format="wav")

    print("fade in and fade out...")
    faded = compressed.fade_in(500).fade_out(650)
    faded.export(f"{output_dir}/faded.wav", format="wav")

    result = normalize(faded)
    result.export(f"{output_dir}/{filename}", format="mp3")

    print(f"Output saved to {output_dir}/{filename}")
    os.remove(f"{output_dir}/noise_reduced.wav")
    os.remove(f"{output_dir}/temp.wav")
    os.remove(f"{output_dir}/normalized.wav")
    os.remove(f"{output_dir}/faded.wav")
    os.remove(f"{output_dir}/compressed.wav")

    print("----------------")
print("Finished.")
