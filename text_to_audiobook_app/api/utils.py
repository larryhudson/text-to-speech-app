from django.conf import settings
import json
import requests
import os.path
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time



MICROSOFT_TTS_REGION = settings.MICROSOFT_TTS_REGION
MICROSOFT_TTS_KEY = settings.MICROSOFT_TTS_KEY
API_BASE_ADDRESS = f'https://{MICROSOFT_TTS_REGION}.customvoice.api.speech.microsoft.com/api/texttospeech/v3.0-beta1'

def synthesise_short_text(text_file):
    print('hello')
    speech_config = SpeechConfig(
        subscription=MICROSOFT_TTS_KEY,
        region=MICROSOFT_TTS_REGION)

    speech_config.speech_synthesis_language = "en-AU"
    speech_config.speech_synthesis_voice_name ="en-AU-NatashaNeural"
    speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat['Audio16Khz64KBitRateMonoMp3'])
    audio_file_path = os.path.join(settings.MEDIA_ROOT, text_file.audio_file_upload_path(None))
    audio_file_folder = os.path.dirname(audio_file_path)

    if not os.path.isdir(audio_file_folder):
        os.makedirs(audio_file_folder)
    
    print(audio_file_path)

    audio_config = AudioOutputConfig(filename=audio_file_path)
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    with open(text_file.file.path) as file:
        text = file.read()
    print(text)
    result = synthesizer.speak_text_async(text)
    return True


def get_synthesis_status(synthesis_id):
    request_url = f'{API_BASE_ADDRESS}/voicesynthesis/{synthesis_id}'

    response = requests.get(
        request_url,
        headers={"Ocp-Apim-Subscription-Key":MICROSOFT_TTS_KEY},
        verify=False
    )
    
    if response.status_code == 200:
        synthesis = json.loads(response.text)
        return synthesis
    else:
        print("getSubmittedSyntheses with ID request failed")
        print("response.status_code: %d" % response.status_code)
        print("response.text: %s" % response.text)
        return None

def submit_synthesis_for_text_file(text_file):
    print('hello!')
    voiceId = 'bcde0279-765d-4336-9647-af83a0ac665d'
    concatenateResult = True
    locale = 'en-AU'
    outputFormat = 'audio-16khz-64kbitrate-mono-mp3'

    synthesisData = {
        'name': text_file.name,
        'description': text_file.description,
        'models': json.dumps([voiceId]),
        'locale': locale,
        'outputformat': outputFormat,
        'properties': json.dumps({
            'ConcatenateResult': 'true' if concatenateResult else 'false'
        })
    }

    filename = os.path.basename(text_file.file.name)

    files = {'script': (filename, open(text_file.file.path, 'rb'), 'text/plain')}

    request_url = f'{API_BASE_ADDRESS}/voicesynthesis'

    response = requests.post(
        request_url,
        synthesisData,
        headers={"Ocp-Apim-Subscription-Key": MICROSOFT_TTS_KEY},
        files=files,
        verify=False)
    
    if response.status_code == 202:
        location = response.headers['Location']
        id = location.split("/")[-1]
        print("Submit synthesis request successful , id: %s" % (id))
        return id
    else:
        print("Submit synthesis request failed")
        print("response.status_code: %d" % response.status_code)
        print("response.text: %s" % response.text)
        return False

def submit_ocr_request(image_path):
    computervision_client = ComputerVisionClient(
        settings.MICROSOFT_CV_ENDPOINT,
        CognitiveServicesCredentials(settings.MICROSOFT_CV_KEY)
    )

    image_file = open(image_path, "rb")

    read_response = computervision_client.read_in_stream(image_file, raw=True)

    read_operation_location = read_response.headers["Operation-Location"]

    operation_id = read_operation_location.split("/")[-1]
    print(f'operation id: {operation_id}')
    return operation_id

def get_ocr_result(operation_id):
    computervision_client = ComputerVisionClient(
        settings.MICROSOFT_CV_ENDPOINT,
        CognitiveServicesCredentials(settings.MICROSOFT_CV_KEY)
    )

    read_result = computervision_client.get_read_result(operation_id)

    if read_result.status == OperationStatusCodes.succeeded:
        lines = []
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                lines.append(line.text)
    return '\n'.join(lines)