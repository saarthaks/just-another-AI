import os
import pyaudio
import pygame
import pyvona
import pydub


class Speaker():

    def __init__(self):
        self.tts_key = 'GDNAIYYXW4K6RQOTDTWQ'
        self.tts_secret = 'dv9b0xvwM8pmiERPvCj+DDSfdccnt/Flw/3ZlBRN'
        self.voice = 'Brian'
        self._audio = pyaudio.PyAudio()

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
        temp_path = "/home/pi/Projects/alfred/just-another-AI/tester/response.mp3"
        v.fetch_voice(text, temp_path)

        return temp_path
    
    def say(self, text):
        fp = self.make_wav(text)
        self.play(fp)
        return

    def ask(self, text):
        self.say(text)
        return raw_input(text).split()
