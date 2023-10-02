from playsound import playsound
import time
import wave

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import simpleaudio as sa

# Replace 'your_sound_file.wav' with the path to your sound file
sound_file = "short-open-hi-hat.wav"

# Load the sound file using pydub
# audio = AudioSegment.empty()
# audio.overlay(AudioSegment.from_file('short-open-hi-hat.wav'))
hihat = AudioSegment.from_file('short-open-hi-hat.wav')
bassdrum = AudioSegment.from_file('bass-drum-hit.wav')

song = AudioSegment.silent(duration=3000)
song = song.overlay(hihat, position=0)
song = song.overlay(bassdrum, position=1000)

# Play the audio using simpleaudio
while True:
    # sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
    _play_with_simpleaudio(song)
    time.sleep(0.5)