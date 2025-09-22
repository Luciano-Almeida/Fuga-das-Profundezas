import wave
import struct
import math

def generate_levelup(filename="levelup.wav", duration=0.6, freq_start=440, freq_end=880, samplerate=44100):
    n_samples = int(samplerate * duration)
    amplitude = 32767
    wav_file = wave.open(filename, 'w')
    wav_file.setparams((1, 2, samplerate, n_samples, "NONE", "not compressed"))

    for i in range(n_samples):
        # Frequência vai subindo durante a duração
        t = i / n_samples
        freq = freq_start + (freq_end - freq_start) * t
        value = int(amplitude * math.sin(2 * math.pi * freq * (i / samplerate)))
        wav_file.writeframes(struct.pack('<h', value))

    wav_file.close()
    print(f"Arquivo gerado: {filename}")

# Gerar o som
generate_levelup("levelup.wav")
