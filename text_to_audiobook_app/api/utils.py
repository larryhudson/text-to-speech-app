from django.conf import settings
import os.path
import re
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig

import os
from pydub import AudioSegment
import asyncio

MICROSOFT_TTS_REGION = settings.MICROSOFT_TTS_REGION
MICROSOFT_TTS_KEY = settings.MICROSOFT_TTS_KEY
API_BASE_ADDRESS = f'https://{MICROSOFT_TTS_REGION}.customvoice.api.speech.microsoft.com/api/texttospeech/v3.0-beta1'


def break_text_into_chunks(full_text, max_chunk_size=7000):
    """
    Break text string into an array of strings, no bigger than the preferred chunk size
    """

    chunks = []
    current_chunk_length = 0
    current_chunk_sentences = []

    sentences = re.split('\. |\.\\n', full_text)

    for sentence in sentences:
        if current_chunk_length + len(sentence) > max_chunk_size:
            # this chunk is done, join it together
            chunk_text = '.\n'.join(current_chunk_sentences)
            chunks.append(chunk_text)
            current_chunk_sentences = []
            current_chunk_length = 0
        else:
            current_chunk_sentences.append(sentence)
            current_chunk_length += len(sentence)

    # add the remaining text as the last chunk
    chunk_text = '.\n'.join(current_chunk_sentences)
    chunks.append(chunk_text)

    return chunks

def join_mp3_files(mp3_paths, joined_mp3_path):
    """
    Combine an array of MP3 files and output a single MP3 file
    """

    combined_audio_segments = AudioSegment.empty()

    for mp3_path in mp3_paths:
        audio_segment = AudioSegment.from_file(mp3_path)
        combined_audio_segments += audio_segment

    print('Exporting joined MP3 to path:')
    print(joined_mp3_path)

    combined_audio_segments.export(joined_mp3_path, format="mp3")

    return joined_mp3_path

async def synthesise_text_file(text_file):

    with open(text_file.file.path) as file:
        text = file.read()

    audio_file_path = os.path.join(settings.MEDIA_ROOT, text_file.audio_file_upload_path(None))

    audio_file_folder = os.path.dirname(audio_file_path)

    if not os.path.isdir(audio_file_folder):
        os.makedirs(audio_file_folder)

    if len(text) < 7000:
        synthesised_audio_file = await synthesise_short_text(text, audio_file_path)
        return True

    else:
        chunks = break_text_into_chunks(text, 7000)
        audio_file_folder = os.path.dirname(audio_file_path)

        chunk_mp3_paths = []
        
        chunk_tuples = []

        for chunk_index, chunk_text in enumerate(chunks):
            chunk_mp3_path = os.path.join(audio_file_folder, f'chunk_{chunk_index}.mp3')
            chunk_mp3_paths.append(chunk_mp3_path)
            chunk_tuples.append(
                (chunk_text, chunk_mp3_path)
            )

        await asyncio.gather(*[synthesise_short_text_async(chunk_text, chunk_mp3_path) for chunk_text, chunk_mp3_path in chunk_tuples])

        joined_mp3_files = join_mp3_files(chunk_mp3_paths, audio_file_path)
        return True

async def synthesise_short_text_async(*args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, synthesise_short_text, *args)

def synthesise_short_text(text_string, audio_file_path):

    speech_config = SpeechConfig(
        subscription=MICROSOFT_TTS_KEY,
        region=MICROSOFT_TTS_REGION)

    print(f'Synthesising {len(text_string)} characters to output path:')
    print(audio_file_path)
    speech_config.speech_synthesis_language = "en-AU"
    speech_config.speech_synthesis_voice_name ="en-AU-NatashaNeural"
    speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat['Audio16Khz64KBitRateMonoMp3'])
    
    audio_config = AudioOutputConfig(filename=audio_file_path)
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text(text_string)
    print('Done synthesising for path:')
    print(audio_file_path)
    return audio_file_path