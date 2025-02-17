"""
Module downloading and parsing voting data from EP webpage.
"""
import os
import time
import xml.etree.ElementTree as ET
import csv
import requests
import pandas as pd
from tqdm import tqdm

def get_term(date):
    """
    Determine the parliamentary term based on the date.
    """
    date_ranges = {
        ("2019-07-02", "2024-07-01"): 9,
        ("2024-07-02", "2029-07-01"): 10,
    }
    for (start_date, end_date), code in date_ranges.items():
        if pd.to_datetime(start_date) <= date <= pd.to_datetime(end_date):
            return code
    return None

def build_url_vote(term, date):
    """
    Build the URL for voting data based on term and date.
    """
    date_str = date.strftime('%Y-%m-%d')
    return f"https://www.europarl.europa.eu/doceo/document/PV-{term}-{date_str}-RCV_EN.xml"

def initialize_log(output_dir):
    """
    Initialize or load the download log.
    """
    log_path = os.path.join(output_dir, 'download_log_voting.csv')
    if os.path.exists(log_path):
        existing_log = pd.read_csv(log_path)
        if 'Status' not in existing_log.columns or 'Date' not in existing_log.columns:
            print("Log file format is invalid. Reinitializing log.")
            existing_log = pd.DataFrame(columns=['Date', 'Status', 'Details'])
    else:
        existing_log = pd.DataFrame(columns=['Date', 'Status', 'Details'])
    return log_path, existing_log

def save_log(log_writer, date_str, status, details):
    """
    Save a log entry to the CSV log file.
    """
    log_writer.writerow([date_str, status, details])

def download_votings(output_dir, start_date, end_date):
    """
    Download voting data and save it into the 'voting' directory.
    """
    os.makedirs(os.path.join(output_dir, "voting"), exist_ok=True)
    log_path, existing_log = initialize_log(output_dir)

    with open(log_path, 'a', newline='', encoding='utf-8') as log_file:
        log_writer = csv.writer(log_file)
        if os.stat(log_path).st_size == 0:
            log_writer.writerow(['Date', 'Status', 'Details'])

        for date in tqdm(pd.date_range(start=start_date, end=end_date, freq='D'), desc="Downloading voting data"):
            date_str = date.strftime('%Y-%m-%d')
            if date_str in set(existing_log.loc[existing_log['Status'] == 'Success', 'Date']) or \
               date_str in set(existing_log.loc[existing_log['Status'] == 'Not Found', 'Date']):
                continue

            try:
                term = get_term(date)
                if not term:
                    save_log(log_writer, date_str, 'Failed', 'Term not found')
                    continue

                response = requests.get(build_url_vote(term, date), timeout=10)
                time.sleep(0.1)

                if response.status_code == 200:
                    file_path = os.path.join(output_dir, "voting", f"PV-{term}-{date_str}.xml")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    save_log(log_writer, date_str, 'Success', 'Downloaded')
                elif response.status_code == 404:
                    save_log(log_writer, date_str, 'Not Found', 'URL not found')
                else:
                    save_log(log_writer, date_str, 'Failed', f'HTTP {response.status_code}')

            except requests.exceptions.RequestException as e:
                save_log(log_writer, date_str, 'Request Error', str(e))

            except OSError as e:
                save_log(log_writer, date_str, 'File Error', str(e))
            except ValueError as e:
                save_log(log_writer, date_str, 'Value Error', str(e))

def save_to_csv(data, output_file):
    """Save the combined voting data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Voting data saved to {output_file}")

def parse_single_file(file_path):
    """Parse a single XML file and return the voting data as a list of dictionaries."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    session_date = root.attrib.get("Sitting.Date", "Unknown Date")
    file_data = []

    for roll_call in root.findall('.//RollCallVote.Result'):
        description = roll_call.find('RollCallVote.Description.Text').text or "No Description"

        for result in roll_call:
            vote_type = result.tag.split(".")[-1]

            for group in result.findall('Result.PoliticalGroup.List'):
                group_id = group.attrib.get("Identifier", "NaN")

                for member in group.findall("PoliticalGroup.Member.Name"):
                    mep_id = member.attrib.get("PersId", "NaN")
                    mep_name = member.text or "NaN"
                    file_data.append({
                        "Date": session_date,
                        "Description": description,
                        "Vote": vote_type,
                        "PoliticalGroup": group_id,
                        "MEP_ID": mep_id,
                        "Name": mep_name
                    })

    return file_data

def parse_votings(input_dir, output_file):
    """Parse XML voting data and save it to a combined CSV."""
    files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    combined_data = []
    for file in tqdm(files, desc="Processing voting files"):
        file_path = os.path.join(input_dir, file)
        try:
            combined_data.extend(parse_single_file(file_path))
        except ET.ParseError as e:
            print(f"XML parsing error in file {file}: {e}")
        except OSError as e:
            print(f"File error with {file}: {e}")

    if combined_data:
        save_to_csv(combined_data, output_file)
    else:
        print("No voting data parsed. Combined CSV not created.")
