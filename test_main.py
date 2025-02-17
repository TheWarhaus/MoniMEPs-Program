"""
Module to test functions used in the program.
"""
import os
from unittest.mock import patch
from datetime import datetime
import filecmp
import pandas as pd
import pytest
from codes.speech import (
    get_term, build_url, download_speeches,
    calculate_duration, parse_speeches, split_text_into_chunks
)
from codes.voting import(
    build_url_vote, download_votings, parse_votings
)
from codes.analysis import (
    analyze_summary_statistics, analyze_summary_statistics_with_respect_to_mep,
    summarize_specific_mep, summarize_voting_statistics,
    summarize_voting_statistics_mep
)
from codes.helpfunc import (
    validate_date_input, validate_yes_no_input, handle_invalid_input,
    choose_mep, retrieve_mep_id
)

current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.join(current_dir, "tests")
test_output_dir = os.path.join(tests_dir, "test_speeches")
test_output_dir_vote = os.path.join(tests_dir, "test_voting")

def test_get_term():
    """Function to test get_term from both voting and speech module."""
    date1 = pd.to_datetime("2023-06-15")
    date2 = pd.to_datetime("2025-07-10")
    assert get_term(date1) == 9
    assert get_term(date2) == 10

def test_build_url():
    """Function to test build_url from speech module."""
    term = 9
    date = datetime.strptime("2023-11-21", "%Y-%m-%d")
    assert build_url(term, date) == "https://www.europarl.europa.eu/doceo/document/CRE-9-2023-11-21_EN.xml"

def test_download_speech_file():
    """Function to test download_speech_file from speech module."""
    start_date = pd.to_datetime("2024-01-15")
    end_date = pd.to_datetime("2024-01-15")
    speeches_dir = os.path.join(tests_dir, "speeches")
    download_speeches(test_output_dir, start_date, end_date)
    speeches_speeches = os.path.join(test_output_dir, "speeches")
    downloaded_file = os.path.join(speeches_speeches, "CRE-9-2024-01-15.xml")
    reference_file = os.path.join(speeches_dir, "CRE-9-2024-01-15.xml")
    with open(downloaded_file, 'r', encoding='utf-8') as f:
        downloaded_content = f.read()
    with open(reference_file, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    assert downloaded_content == reference_content

def test_calculate_duration():
    """Function to test calculate_duration from speech module."""
    assert calculate_duration("12:00:00", "12:30:20") == 1820

def test_parse_speeches():
    """Function to test parse_speeches and inserted function within from speech module."""
    reference_file = os.path.join(tests_dir, "parsed_speeches.csv")
    speeches_dir = os.path.join(tests_dir, "speeches")
    output_file = os.path.join(test_output_dir, "test_parsed_speeches.csv")
    parse_speeches(speeches_dir, output_file)
    generated_df = pd.read_csv(output_file)
    reference_df = pd.read_csv(reference_file)
    pd.testing.assert_frame_equal(generated_df, reference_df, check_dtype=False)

def test_log_file_speech():
    """Function to test existence of log_file created when downloading the speeches."""
    created_log_path = os.path.join(test_output_dir, "download_log_speech.csv")
    reference_log = os.path.join(tests_dir, "download_log_speech.csv")
    generated_log = pd.read_csv(created_log_path)
    reference_log_df = pd.read_csv(reference_log)
    pd.testing.assert_frame_equal(generated_log, reference_log_df)

def test_split_text_into_chunks():
    """Function to test split_text_into_chunks from speech module."""
    text = "a" * 12000
    chunks = split_text_into_chunks(text)
    assert all(len(chunk) <= 5000 for chunk in chunks)
    assert "".join(chunks) == text

#translation not tested as it always might generate different text as it uses google translate

def test_build_url_vote():
    """Function to test split_text_into_chunks from voting module."""
    term = 9
    date = datetime.strptime("2023-11-21", "%Y-%m-%d")
    assert build_url_vote(term, date) == "https://www.europarl.europa.eu/doceo/document/PV-9-2023-11-21-RCV_EN.xml"

def test_download_voting_file():
    """Function to test download_voting_file and related functions from voting module."""
    start_date = pd.to_datetime("2024-01-15")
    end_date = pd.to_datetime("2024-01-15")
    voting_dir = os.path.join(tests_dir, "voting")
    download_votings(test_output_dir_vote, start_date, end_date)
    votings_votings = os.path.join(test_output_dir_vote, "voting")
    downloaded_file = os.path.join(votings_votings, "PV-9-2024-01-15.xml")
    reference_file = os.path.join(voting_dir, "PV-9-2024-01-15.xml")
    with open(downloaded_file, 'r', encoding='utf-8') as f:
        downloaded_content = f.read()
    with open(reference_file, 'r', encoding='utf-8') as f:
        reference_content = f.read()
    assert downloaded_content == reference_content

def test_parse_votings():
    """Function to test parse_votings and related functions from voting module."""
    reference_file = os.path.join(tests_dir, "parsed_votings.csv")
    voting_dir = os.path.join(tests_dir, "voting")
    output_file = os.path.join(test_output_dir_vote, "parsed_votings.csv")
    parse_votings(voting_dir, output_file)
    generated_df = pd.read_csv(output_file)
    reference_df = pd.read_csv(reference_file)
    pd.testing.assert_frame_equal(generated_df, reference_df, check_dtype=False)

def test_log_file_voting():
    """Function to test existence of log_file created when downloading the voting data."""
    created_log_path = os.path.join(test_output_dir_vote, "download_log_voting.csv")
    reference_log = os.path.join(tests_dir, "download_log_voting.csv")
    generated_log = pd.read_csv(created_log_path)
    reference_log_df = pd.read_csv(reference_log)
    pd.testing.assert_frame_equal(generated_log, reference_log_df)

def test_analyze_summary_statistics():
    """Function to test analyze_summary_statistics from analysis module."""
    analysis_output_dir = os.path.join(test_output_dir, "analysis")
    input_df = os.path.join(tests_dir, "translated_speeches.csv")
    reference_analysis_dir = os.path.join(tests_dir, "analysis")
    dataframe = pd.read_csv(input_df)
    analyze_summary_statistics(dataframe, analysis_output_dir)
    mismatched_files = []
    for file_name in os.listdir(reference_analysis_dir):
        generated_file = os.path.join(analysis_output_dir, file_name)
        reference_file = os.path.join(reference_analysis_dir, file_name)
        if not filecmp.cmp(generated_file, reference_file, shallow=False):
            mismatched_files.append(file_name)
    assert not mismatched_files

def test_analyze_summary_statistics_with_respect_to_mep():
    """Function to test analyze_summary_statistics_with_respect_to_mep from analysis module."""
    analysis_output_dir = os.path.join(test_output_dir, "analysis_mep")
    input_df = os.path.join(tests_dir, "translated_speeches.csv")
    reference_analysis_dir = os.path.join(tests_dir, "analysis_mep")
    mep_name = "Roberta Metsola"
    dataframe = pd.read_csv(input_df)
    analyze_summary_statistics_with_respect_to_mep(dataframe, mep_name, analysis_output_dir)
    mismatched_files = []
    for file_name in os.listdir(reference_analysis_dir):
        generated_file = os.path.join(analysis_output_dir, file_name)
        reference_file = os.path.join(reference_analysis_dir, file_name)
        if not filecmp.cmp(generated_file, reference_file, shallow=False):
            mismatched_files.append(file_name)
    assert not mismatched_files

def test_summarize_specific_mep(capsys):
    """Function to test summarize_specific_mep from analysis module."""
    input_csv_path = os.path.join(tests_dir, "translated_speeches.csv")
    dataframe = pd.read_csv(input_csv_path)
    mep_name = "Roberta Metsola"
    expected_summary = (
        "\nSummary Statistics for Roberta Metsola:\n"
        "Total number of speeches: 30\n"
        "Total time of speeches: 1534.00 seconds\n"
        "Average time of speech: 51.13 seconds\n"
        "Average length of speech: 93.43 words\n"
    )
    summarize_specific_mep(dataframe, mep_name)
    captured = capsys.readouterr()
    assert captured.out == expected_summary

def test_summarize_voting_statistics(capsys):
    """Function to test summarize_voting_statistics from analysis module."""
    input_csv_path = os.path.join(tests_dir, "parsed_votings.csv")
    dataframe = pd.read_csv(input_csv_path)
    expected_summary = (
        "\nSummary Statistics for Voting Data:\n"
        "Total number of votings: 7\n"
        "Votings accepted: 6\n"
        "Votings rejected: 1\n"
    )
    summarize_voting_statistics(dataframe)
    captured = capsys.readouterr()
    assert captured.out == expected_summary

def test_summarize_voting_statistics_mep(capsys):
    """Function to test summarize_voting_statistics_mep from analysis module."""
    input_csv_path = os.path.join(tests_dir, "parsed_votings.csv")
    dataframe = pd.read_csv(input_csv_path)
    mep_name = "Nicola Procaccini"
    selected_mep_id = 197820
    expected_summary = (
        "\nSummary Statistics for Nicola Procaccini:\n"
        "Total number of votes: 6\n"
        "Votes For: 3\n"
        "Votes Against: 1\n"
        "Votes Abstain: 2\n"
        "Number of absences from voting: 1\n"
    )
    summarize_voting_statistics_mep(dataframe, mep_name, selected_mep_id)
    captured = capsys.readouterr()
    assert captured.out == expected_summary

def test_validate_date_input():
    """Function to test validate_date_input from helpfunc module."""
    import datetime
    with patch("builtins.input", side_effect=["12345", "15-01-2025", "2025-01-15"]):
        result = validate_date_input("Enter a date (YYYY-MM-DD): ")
        assert result == datetime.date(2025, 1, 15)

def test_validate_yes_no_input():
    """Function to test validate_yes_no_input from helpfunc module."""
    with patch("builtins.input", side_effect=["maybe", "123", "yes"]):
        result = validate_yes_no_input("Do you want to continue? (yes/no): ")
        assert result == "yes"
    with patch("builtins.input", side_effect=["nope", "NO"]):
        result = validate_yes_no_input("Do you want to continue? (yes/no): ")
        assert result == "no"

def test_handle_invalid_input():
    """Function to test handle_invalid_input from helpfunc module."""
    valid_choices = ["apple", "banana", "cherry"]
    with patch("builtins.input", side_effect=["orange", "123", "banana"]):
        result = handle_invalid_input("Choose a fruit (apple/banana/cherry): ", valid_choices)
        assert result == "banana"
    with patch("builtins.input", side_effect=["APPLE", "apple"]):
        result = handle_invalid_input("Choose a fruit (apple/banana/cherry): ", valid_choices)
        assert result == "apple"

def test_choose_mep():
    """Function to test choose_mep from helpfunc module."""
    input_csv_path = os.path.join(tests_dir, "translated_speeches.csv")
    dataframe = pd.read_csv(input_csv_path)
    def mock_input(prompt):
        if prompt.startswith("Enter part of the MEP's name"):
            return "metsola"
        if prompt.startswith("Select the number of the MEP"):
            return "1"
        return ""
    with patch('builtins.input', side_effect=mock_input):
        selected_name = choose_mep(dataframe, 'Speaker Name')
    assert selected_name == "Roberta Metsola"

def test_retrieve_mep_id():
    """Function to test retrieve_mep_id from helpfunc module."""
    input_csv_path = os.path.join(tests_dir, "translated_speeches.csv")
    dataframe = pd.read_csv(input_csv_path)
    selected_mep = "Leila Chaibi"
    result = retrieve_mep_id(dataframe, selected_mep)

    assert result == 197529

# menu functions tested manually while running the program

if __name__ == "__main__":
    pytest.main()
