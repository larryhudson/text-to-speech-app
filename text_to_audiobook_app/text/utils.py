import textract
import trafilatura
import os

def extract_text(file, **options):
    text = textract.process(file, method='tesseract').decode('utf8')
    if file.endswith('.pdf'):
        text = text.replace('-\n', '')

        text = text.replace('\n\n', '[LINEBREAK]')
        text = text.replace('\n', ' ')

        text = text.replace('[LINEBREAK]', '\n')
    return text

def extract_text_from_url(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text

def write_text_to_file(text_string, file_path):
        file_folder = os.path.dirname(file_path)

        if not os.path.isdir(file_folder):
            os.makedirs(file_folder)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text_string)

        return True
