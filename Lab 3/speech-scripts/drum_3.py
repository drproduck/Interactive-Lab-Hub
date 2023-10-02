#!/usr/bin/env python3

# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import json
import time
from pynput import keyboard
import sounddevice as sd

from vosk import Model, KaldiRecognizer
from playsound import playsound
from gtts import gTTS
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

from multiprocessing import Process

# Play the audio using simpleaudio

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

mp3_fp = BytesIO()
# tts = gTTS('Hello! I am a drum machine that can play hi hat, bass drum and snare drum sounds. ', lang='en')
tts = gTTS('Hello!', lang='en')
tts.save('hello.wav')

# tts = gTTS("Sorry, I don't recognize the instrument you are saying.", lang='en')
tts = gTTS("Sorry.", lang='en')
tts.save('sorry.wav')


###############################################################
# LOOP


sounds = {
    'hi-hat': AudioSegment.from_file('short-open-hi-hat.wav'),
    'snare-drum': AudioSegment.from_file('wide-snare-drum_B_minor.wav'),
    'base-drum': AudioSegment.from_file('bass-drum-hit.wav'),
    'hello': AudioSegment.from_file('hello.wav'),
    'sorry': AudioSegment.from_file('sorry.wav'),
}

_play_with_simpleaudio(sounds['hello'])

def get_sound_name(rec, data):
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())["text"]
        if (result.find("hi hat") != -1):
            print("Switching to hi hat.")
            return "hi-hat"
            # playsound("short-open-hi-hat.wav")
        elif (result.find("snare drum") != -1): 
            print("Switching to snare drum.")
            return "snare-drum"
            # playsound("wide-snare-drum_B_minor.wav")
        elif (result.find("bass drum") != -1):
            print("Switching to bass drum.")
            return "bass-drum"
            # playsound("bass-drum-hit.wav")

    return ""

##############################
# keyboard

##############################
sound_name = ""

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])
        
    if args.model is None:
        model = Model(lang="en-us")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate, '["bass", "snare", "drum", "hi", "hat", "start", "[unk]"]')
        last_sorry_playback_time = 0


        start_time = 0
        time_list = []

        # playlist = []

        start_time = time.time()
        interval_duration = 3 # second
        curr_interval = 0

        song = AudioSegment.silent(duration=interval_duration * 1000)

        def on_press(key):
            global song
            if key == keyboard.Key.space and sound_name != "":
                _play_with_simpleaudio(sounds[sound_name])
                song = song.overlay(sounds[sound_name], position=1000 * (curr_time % interval_duration))

        listener = keyboard.Listener(
            on_press=on_press,
        )

        listener.start()

        while True:
            data = q.get()
            temp_sound_name = get_sound_name(rec, data)
            if temp_sound_name != "":
                sound_name = temp_sound_name

            curr_time = time.time()

            this_interval = (curr_time - start_time) // interval_duration
            if this_interval > curr_interval:
                curr_interval = this_interval

                # start playing. does it block?
                _play_with_simpleaudio(song)



except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
