import RPi.GPIO as GPIO
import time,os,sys
import pyaudio,audioop,wave,math
from collections import deque
import requests,json
from xml.etree import ElementTree
import pygame

chan_list = [29,31,33]

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 15
THRESHOLD = 2500  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.
WAVE_OUTPUT_FILENAME = "output.wav"
os.close(sys.stderr.fileno())

try: input = raw_input
except NameError: pass

subscription_key = "582eb7d4c2ce413ca01dd8823c14b320"

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(chan_list, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    for pin in chan_list:
        GPIO.add_event_detect(pin, GPIO.BOTH,bouncetime=150)
    pygame.mixer.init()

def record(pin,threshold=THRESHOLD):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Listening mic. ")
    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=int(PREV_AUDIO * rel)) 
    started = False
    response = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        if GPIO.event_detected(pin):
            break

        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

        if(sum([x > THRESHOLD for x in slid_win]) > 0):
            if(not started):
                print("Starting record of phrase")
                started = True
            audio2send.append(cur_data)
        else:
            prev_audio.append(cur_data)

    if started == True:
        print("Finished")
        # The limit was reached, finish capture and deliver.
        filename = save_speech(list(prev_audio) + audio2send, p)
        started = False
        slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
        prev_audio = deque(maxlen=int(0.5 * rel)) 
        audio2send = []
        print("* Done recording")
        stream.close()
        p.terminate()

    return started

def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """

    filename = 'output'
    # writes data to WAV file
    data = b''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'

def getanser(question,pin):
    url = "http://140.120.13.252:81/predict"

    payload = {"question":question,"id":pin}
    headers = {
        'Content-Type': "application/json",
        }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    result=response.json()
    print(result)
    return result['best_span_str']

class cognitive(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None

    def get_token(self):
        fetch_token_url = "https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def TextToSpeech(self,tts):
        base_url = 'https://eastasia.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'voice'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)')
        voice.text = tts
        body = ElementTree.tostring(xml_body)
        response = requests.post(constructed_url, headers=headers, data=body)

        if response.status_code == 200:
            with open('temp.wav', 'wb') as audio:
                audio.write(response.content)
                audio.close()
                pygame.mixer.music.load("temp.wav")
                pygame.mixer.music.play()
                print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")

    def SpeechToText(self):
        base_url = 'https://eastasia.stt.speech.microsoft.com/'
        path = 'speech/recognition/conversation/cognitiveservices/v1?language=zh-TW'
        querystring = {"language":"zh-TW","format":"detailed"}
        data = open('output' + '.wav','rb').read()
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Accept': 'application/json;text/xml',
            'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
            'User-Agent': 'voice',
            # 'Ocp-Apim-Subscription-Key':subscription_key
        }
        response=requests.post(constructed_url, headers=headers, data=data)
        if response.status_code == 200:
            result=response.json()
            print(result)
            print("\nStatus code: " + str(response.status_code) + "\nYour STT is ready for playback.\n")
            return result['DisplayText']
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
            return 0

if __name__ == "__main__":
    setup()
    app = cognitive(subscription_key)
    app.get_token()
    try:
        while True:
            if GPIO.event_detected(chan_list[0]):
                record(chan_list[0])
                result=getanser(app.SpeechToText(),0)
                app.TextToSpeech(result)
                app.get_token()
            if GPIO.event_detected(chan_list[1]):
                record(chan_list[1])
                # result=getanser(app.SpeechToText(),1)
                app.TextToSpeech(app.SpeechToText())
                app.get_token()
            if GPIO.event_detected(chan_list[2]):
                record(chan_list[2])
                result=getanser(app.SpeechToText(),2)
                app.TextToSpeech(result)
                app.get_token()
            pass
    except Exception as e:
        GPIO.cleanup()
        print('cleanup')
        print('Reason:', e)