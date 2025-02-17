"""
Module to download and parse speech files.
"""
import os
import time
import csv
import re
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import pandas as pd
from tqdm import tqdm
from langdetect import detect
from googletrans import Translator

def get_term(date):
    """Determine the parliamentary term based on the date."""
    date_ranges = {
        ("2019-07-02", "2024-07-01"): 9,
        ("2024-07-02", "2029-07-01"): 10
    }
    for (start_date, end_date), code in date_ranges.items():
        if pd.to_datetime(start_date) <= date <= pd.to_datetime(end_date):
            return code
    return None

def build_url(term, date):
    """
    Build the URL for speeches based on term and date.
    """
    date_str = date.strftime('%Y-%m-%d')
    return f"https://www.europarl.europa.eu/doceo/document/CRE-{term}-{date_str}_EN.xml"

def initialize_log(log_path):
    """
    Initialize or load the download log file.
    """
    if os.path.exists(log_path):
        log_df = pd.read_csv(log_path)
        if 'Status' not in log_df.columns or 'Date' not in log_df.columns:
            print("Log file format is invalid. Reinitializing log.")
            log_df = pd.DataFrame(columns=['Date', 'Status', 'Details'])
    else:
        log_df = pd.DataFrame(columns=['Date', 'Status', 'Details'])
    return log_df

def save_speech_file(speeches_dir, term, date_str, content):
    """
    Save the speech file to the speeches directory.
    """
    filename = f"CRE-{term}-{date_str}.xml"
    file_path = os.path.join(speeches_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def handle_download(date, date_str, speeches_dir, log_writer):
    """
    Handle the download of a single date's speeches.
    """
    try:
        term = get_term(date)
        if not term:
            log_writer.writerow([date_str, 'Failed', 'Term not found'])
            return

        url = build_url(term, date)
        response = requests.get(url, timeout=10)
        time.sleep(0.1)

        if response.status_code == 200:
            save_speech_file(speeches_dir, term, date_str, response.text)
            log_writer.writerow([date_str, 'Success', 'Downloaded'])
        elif response.status_code == 404:
            log_writer.writerow([date_str, 'Not Found', 'URL not found'])
        else:
            log_writer.writerow([date_str, 'Failed', f'HTTP {response.status_code}'])

    except requests.exceptions.RequestException as e:
        log_writer.writerow([date_str, 'Request Error', str(e)])

def download_speeches(output_dir, start_date, end_date):
    """
    Download speeches within the given date range and save them into a 'speeches' directory.
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    speeches_dir = os.path.join(output_dir, "speeches")
    os.makedirs(speeches_dir, exist_ok=True)

    log_path = os.path.join(output_dir, 'download_log_speech.csv')
    log_df = initialize_log(log_path)

    processed_dates = set(log_df.loc[log_df['Status'] == 'Success', 'Date'])
    not_found_dates = set(log_df.loc[log_df['Status'] == 'Not Found', 'Date'])

    with open(log_path, 'a', newline='', encoding='utf-8') as log_file:
        log_writer = csv.writer(log_file)

        if os.stat(log_path).st_size == 0:
            log_writer.writerow(['Date', 'Status', 'Details'])

        for date in tqdm(dates, desc="Downloading speeches"):
            date_str = date.strftime('%Y-%m-%d')
            if date_str in processed_dates or date_str in not_found_dates:
                continue
            handle_download(date, date_str, speeches_dir, log_writer)

def gather_text(element):
    """
    Recursively gather text from an XML element.
    """
    parts = []
    skip_phrases_pattern = re.compile(r"^(on behalf of|en nombre del|au nom du|a nome|namens de) ", re.IGNORECASE)
    note_pattern = re.compile(r"^\(.*\)$")
    if element.text:
        parts.append(element.text.strip())
    for child in element:
        if child.tag == "EMPHAS" and child.text:
            text = child.text.strip()
            if skip_phrases_pattern.match(text) or note_pattern.match(text):
                continue
        parts.append(gather_text(child))
        if child.tail:
            parts.append(child.tail.strip())
    return " ".join(filter(None, parts))

def calculate_duration(time_start, time_end):
    """
    Calculate the duration in seconds between two time strings.
    """
    fmt = "%H:%M:%S"
    try:
        start = datetime.strptime(time_start.split('.')[0], fmt)
        end = datetime.strptime(time_end.split('.')[0], fmt)
        return (end - start).seconds
    except ValueError:
        return None

def speech_parse(speech, date, time_start, time_end, topic):
    """Extract structured speech data from an INTERVENTION element."""
    text, mepid, speaker_name, party, speaker_type = "", "NaN", "NaN", "NaN", "NaN"
    text_parts = []
    for para in speech.findall("PARA"):
        if gather_text(para):
            text_parts.append(gather_text(para))
    text = " ".join(text_parts)
    if ". – " in text:
        text = text.split(". – ", 1)[1].strip()
    text = text.lstrip("– ").strip()
    if speech.find("ORATEUR") is not None:
        mepid = speech.find("ORATEUR").get("MEPID", "NaN")
        party = speech.find("ORATEUR").get("PP", "NaN")
        speaker_type = speech.find("ORATEUR").get("SPEAKER_TYPE", "NaN")
        if speech.find("ORATEUR").get("LIB", "NaN") != "NaN" and " | " in speech.find("ORATEUR").get("LIB", "NaN"):
            last_name, first_name = speech.find("ORATEUR").get("LIB", "NaN").split(" | ")
            speaker_name = f"{last_name} {first_name}"
        else:
            speaker_name = speech.find("ORATEUR").get("LIB", "NaN")
    duration = calculate_duration(time_start, time_end)
    return {
        "Date": date,
        "Time Start": time_start,
        "Time End": time_end,
        "Duration": duration,
        "Topic": topic,
        "Text": text,
        "MEPID": mepid,
        "Speaker Name": speaker_name,
        "Party": party,
        "Speaker Type": speaker_type
    }

def parse_speeches(input_dir, output_file):
    """Parse XML content from .xml files and extract speech data to a combined CSV file."""
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    combined_data = []
    for file in tqdm([f for f in os.listdir(input_dir) if f.endswith('.xml')], desc="Processing files"):
        try:
            tree = ET.parse(os.path.join(input_dir, file))
            root = tree.getroot()
            for chapter in root.findall(".//CHAPTER"):
                topic = chapter.find("TL-CHAP[@VL='EN']").text if chapter.find("TL-CHAP[@VL='EN']") is not None else "Unknown Topic"
                current_date, current_time_start, current_time_end = None, None, None

                for elem in chapter:
                    if elem.tag == "NUMERO" and elem.get("VOD-START") and elem.get("VOD-END"):
                        current_date, current_time_start = elem.get("VOD-START").split("T")
                        current_time_end = elem.get("VOD-END").split("T")[1]
                    elif elem.tag == "INTERVENTION" and current_date and current_time_start and current_time_end:
                        combined_data.append(speech_parse(elem, current_date, current_time_start, current_time_end, topic))
        except (FileNotFoundError, ET.ParseError, AttributeError) as e:
            print(f"Error processing file {file}: {e}")
    if combined_data:
        df = pd.DataFrame(combined_data)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Combined CSV saved to {output_file}")
    else:
        print("No data parsed. Combined CSV was not created.")

translator = Translator()

def split_text_into_chunks(text, max_length=5000):
    """Split text into chunks that are within the maximum length limit."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].strip()
    chunks.append(text)
    return chunks


def translate_text(text):
    """Translate a given text to English, handling long texts and retries."""
    def translate_chunk(chunk, src_lang):
        """Translate a single chunk of text with retries."""
        for attempt in range(3):
            try:
                result = translator.translate(chunk, src=src_lang, dest='en')
                if result and isinstance(result.text, str):
                    time.sleep(0.4)
                    return result.text
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Retrying translation for chunk due to network issue or error for chunk: {e}")
                time.sleep(2 ** attempt)
        return chunk

    try:
        if not isinstance(text, str) or text.strip() == "":
            return text, 0

        detected_language = detect(text)
        if detected_language == 'en':
            return text, 1
        if len(text) > 5000:
            chunks = split_text_into_chunks(text)
            translated_chunks = [translate_chunk(chunk, detected_language) for chunk in chunks]
            return " ".join(translated_chunks), 1

        translated_text = translate_chunk(text, detected_language)
        if translated_text != text:
            return translated_text, 1
        return text, 0

    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"Translation failed due to network-related error or invalid input: {e}")
        return text, 0

def translate_text_file(input_csv_path, output_csv_path):
    """Translate the 'Text' column in a CSV file to English and save results."""
    try:
        df = pd.read_csv(input_csv_path)
        if 'Text' not in df.columns:
            print(f"No 'Text' column found in {input_csv_path}. Skipping translation.")
            return

        df['Text'] = df['Text'].fillna("").astype(str)
        translated_results = []

        print("Translating texts...")
        with tqdm(total=len(df['Text']), desc="Translating", ncols=80) as pbar:
            for text in df['Text']:
                translated_text, _ = translate_text(text)
                translated_results.append(translated_text)
                pbar.update(1)

        df['Translated Text'] = translated_results
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"Translated file saved at: {output_csv_path}")

    except (FileNotFoundError, pd.errors.EmptyDataError, ConnectionError, TimeoutError, ValueError) as e:
        print(f"Error during translation processing: {e}")
