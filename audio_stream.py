import os
import requests
import time
from xml.etree import ElementTree
from pydub import AudioSegment
from pydub.playback import play
import io




try:
    input = raw_input
except NameError:
    pass

class TextToSpeech(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None
    def get_token(self):
        fetch_token_url = "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self,text):
        base_url = 'https://eastus.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set(
            'name', 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)')
        voice.text = text
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            file_name = 'sample-' + self.timestr + '.wav'
            with open(file_name, 'wb') as audio:
                audio.write(response.content)
                self.play_bytes(response.content)
                print("\nStatus code: " + str(response.status_code) +
                      "\nYour TTS is ready for playback.\n")
            #self.real_play(file_name)
        else:
            print("\nStatus code: " + str(response.status_code) +
                  "\nSomething went wrong. Check your subscription key and headers.\n")


    def real_play(self, file):
        data = open(file, 'rb').read()
        song = AudioSegment.from_file(io.BytesIO(data), format="wav")
        play(song)     

    def play_bytes(self, byte_data):
        song = AudioSegment.from_file(io.BytesIO(byte_data), format="wav")     
        play(song)




if __name__ == "__main__":
    subscription_key = "9a230063f45c4838aa7ccdc41c710bdd"
    text_data = input("what do you want to convert ")
    app = TextToSpeech(subscription_key, text_data)
    app.get_token()
    app.save_audio()
