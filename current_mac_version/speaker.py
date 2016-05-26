import os
import sys
sys.path.append("/Users/user/anaconda/bin")
import audioop
import pyaudio
import tempfile
import wave
import pyvona
import pydub

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
MODELDIR = "pocketsphinx/model"
DATADIR = "pocketsphinx/test/data"

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


class Speaker():

    def __init__(self, profile):
        self.THRESHOLD_MULTIPLIER = 1.8
        self.ACTIVE_RATE = 44100
        self.ACTIVE_CHUNK = 512
        self.PASSIVE_RATE = 16000
        self.PASSIVE_CHUNK = 1024

        self.active_key = profile['active-stt-access-key']


        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(DATADIR, 'en-us/en-us'))
        config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
        self.passive_decoder = Decoder(config)

        self.tts_key = profile['tts_key']
        self.tts_secret = profile['tts_secret']
        self.voice = profile['tts_voice']
        self._audio = pyaudio.PyAudio()

    def play(self, file_path):
        f = wave.open(file_path, "rb")

        chunk = 1024
        stream = self._audio.open(ormat = p.get_format_from_width(f.getsampwidth()),
                                  channels = f.getnchannels(),
                                  rate = f.getframerate(),
                                  output = True)

        data = f.readframes(chunk)
        while data != '':
            stream.write(data)
            data = f.readframes(chunk)

        stream.stop_stream()
        stream.close()
        f.close()
        return

    def make_wav(self, text):
        v = pyvona.create_voice()
        v.voice_name = self.voice
        v.codec = 'mp3'
        temp_path = "/Users/user/Projects/alfred/tester/response.mp3"
        v.fetch_voice(text, temp_path)

        final_path = "/Users/user/Projects/alfred/tester/response.wav"
        sound = pydub.AudioSegment.from_mp3(temp_path)
        sound.export(final_path, format='wav')
        os.remove(temp_path)

        return final_path

    def say(self, text):
        path = self.make_wav(text)
        f = wave.open(path, "rb")

        chunk = 1024
        stream = self._audio.open(ormat = p.get_format_from_width(f.getsampwidth()),
                                  channels = f.getnchannels(),
                                  rate = f.getframerate(),
                                  output = True)

        data = f.readframes(chunk)
        while data != '':
            stream.write(data)
            data = f.readframes(chunk)

        stream.stop_stream()
        stream.close()
        f.close()
        os.remove(path)
        return

    def passive_transcribe(self, audio_file):
        audio_file.seek(44)
        self.passive_decoder.decode_raw(audio_file)
        result = self.passive_decoder.get_hyp()
        return result[0]

    def passiveListen(self, persona):
        rate = self.PASSIVE_RATE
        chunk = self.PASSIVE_CHUNK
        LISTEN_TIME = 10

        THRESHOLD = self.THRESHOLD_MULTIPLIER * self.fetchThreshold()
        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=rate,
                                  input=True,
                                  frames_per_buffer=chunk)
        frames = []
        didDetect = False

        for i in range(0, rate / chunk * LISTEN_TIME):

            data = stream.read(chunk)
            frames.append(data)
            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
                break

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            stream.stop_stream()
            stream.close()
            return (None, None)

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1.5
        for i in range(0, rate / chunk * DELAY_MULTIPLIER):
            data = stream.read(chunk)
            frames.append(data)

        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(rate)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            # check if PERSONA was said
            transcribed = self.passive_transcribe(f)

        if any(persona in phrase for phrase in transcribed):
            return (THRESHOLD, persona)

        return (False, transcribed)

    def getScore(self, data):
        return audioop.rms(data, 2) / 3

    def fetchThreshold(self, ACTIVE=False):
        if ACTIVE:
            rate = self.ACTIVE_RATE
            chunk = self.ACTIVE_CHUNK
        else:
            rate = self.PASSIVE_RATE
            chunk = self.PASSIVE_CHUNK

        THRESHOLD_MULTIPLIER = 1.8
        THRESHOLD_TIME = 1

        stream = self._audio.open(format=pyaudio.paInt16,
                                  channel=1,
                                  rate=rate,
                                  input=true,
                                  frames_per_buffer=chunk)
        frames = []

        lastN = [i for i in range(20)]

        for i in range(0, rate / chunk * THRESHOLD_TIME):

            data = stream.read(chunk)
            frames.append(data)

            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        stream.stop_stream()
        stream.close()

        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def activeListenToAllOptions(self, THRESHOLD=None):
        if THRESHOLD is None:
            THRESHOLD = self.fetchThreshold(ACTIVE=True)

        MAX_LISTEN_TIME = 12

        self.play("/Users/user/Projects/alfred/tester/audio_on.wav")

        stream = self._audio.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        ai = apiai.ApiAI(self.active_key)
        request = ai.voice_request()
        request.lang = 'en'

        frames = []
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(30)]

        for i in range(0, self.ACTIVE_RATE / self.ACTIVE_CHUNK * MAX_LISTEN_TIME):

            data = stream.read(self.ACTIVE_CHUNK)
            frames.append(data)
            request.send(data)
            score = self.getScore(data)

            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))

            if average < THRESHOLD * 0.8:
                break

        self.play("/Users/user/Projects/alfred/tester/audio_off.wav")

        stream.stop_stream()
        stream.close()
        response = request.getresponse()

        return response

    def ask(self, text):

        if text == "Initial Ask":
            self.play("/Users/user/Projects/alfred/tester/Initial_Ask.mp3")
        elif text == "Continuing Ask":
            self.play("/Users/user/Projects/alfred/tester/Continuing_Ask.mp3")
        elif text == "Ending Ask":
            self.play("/Users/user/Projects/alfred/tester/Ending_Ask.mp3")
        else:
            self.say(text)

        response = self.activeListenToAllOptions()
        return response

    def close(self):
        self.play("/Users/user/Projects/alfred/tester/Close.mp3")
        return