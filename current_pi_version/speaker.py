import os
import sys
import alfredpath
import pyaudio
import audioop
import wave
import pygame
import pyvona
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai
from codecs import open
import json
import atexit

class Speaker():

    def __init__(self, profile):
        self.stt_key = profile['active_stt_key']
        ai = apiai.ApiAI(self.stt_key)
        self.stt_request = ai.voice_request()
        self.stt_request.lang = 'en'

        self.tts_key = profile['tts_key']
        self.tts_secret = profile['tts_secret']
        self.voice = ['tts_voice']
        self._audio = pyaudio.PyAudio()

        atexit.register(lambda: self._audio.terminate())

    def play(self, file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        return

    def make_wav(self, text):
        v = pyvona.create_voice(self.tts_key, self.tts_secret)
        v.voice_name = self.voice
        v.codec = 'mp3'
        temp_path = alfredpath.pi_builder('response.mp3')
        v.fetch_voice(text, temp_path)

        return temp_path

    def say(self, text):
        if text == "Sorry":
            self.play(alfredpath.pi_builder('Sorry.mp3'))
            return
        elif text == "Exit":
            self.play(alfredpath.pi_builder('Exit.mp3'))
            return

        fp = self.make_wav(text)
        self.play(fp)
        return

    def getScore(self, data):
        return audioop.rms(data, 2) * 100

    def fetchThreshold(self):
        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = 1
        INPUT_DEVICE_INDEX = 2

        stream = self._audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=INPUT_DEVICE_INDEX)

        print("* recording for threshold")

        frames = []

        lastN = [i for i in range(20)]

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        print("* done recording for threshold")

        stream.stop_stream()
        stream.close()
        return average * 1.8

    def record_audio(self):
        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = 10
        INPUT_DEVICE_INDEX = 2
        THRESHOLD = self.fetchThreshold()

        stream = self._audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=INPUT_DEVICE_INDEX)

        print("* recording")

        frames = []
        lastN = [THRESHOLD * 1.2 for i in range(250)]

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)
            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))
            print average

            if average < THRESHOLD * 0.8:
                break

        print("* done recording")

        stream.stop_stream()
        stream.close()
        #p.terminate()
        return frames

    def make_file(self, frames):
        f = "query.wav"
        wf = wave.open(f, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self._audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(48000)
        wf.writeframes(b''.join(frames))
        wf.close()
        return f

    def get_stt_response(self, fp):
        bytessize = 2048
        with open(fp, 'rb') as f:
            data = f.read(2048)
            while data:
                self.stt_request.send(data)
                data = f.read(2048)

        response = self.stt_request.getresponse()
        resp = response.read()
        resp2 = json.loads(resp)
        return resp2["result"]["resolvedQuery"]

    def ask(self, text):
        self.say(text)
        return self.get_stt_response(self.make_file(self.record_audio())).split()

    def close(self):
        self.play(alfredpath.pi_builder('Exit.mp3'))
        return