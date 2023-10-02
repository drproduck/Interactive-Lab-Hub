from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

# # song = AudioSegment.silent(duration=3)
# song = AudioSegment.empty()
# # song.overlay(AudioSegment.from_file("short-open-hi-hat.wav"), position=0)
# song += AudioSegment.from_file("short-open-hi-hat.wav")
# _play_with_simpleaudio(song)
_play_with_simpleaudio(AudioSegment.from_file("short-open-hi-hat.wav"))