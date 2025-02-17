"""
Modul with help functions used in main module.
"""

import shutil
import os
import stat
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from codes.analysis import (
    analyze_summary_statistics, analyze_specific_words, summarize_voting_statistics,
    analyze_summary_statistics_with_respect_to_mep, analyze_specific_words_filtered_by_mep,
    summarize_voting_statistics_mep

)


def delete_existing_data(output_dir):
    """Delete all files in the output directory with permission handling."""
    if os.path.exists(output_dir):
        confirm = input(f"Are you sure you want to delete all data in '{output_dir}'? (yes/no): ").strip().lower()
        if confirm == 'yes':

            def on_rm_error(func, path, exc_info):
                """Handle errors during removal by changing permissions and retrying."""
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise exc_info[1]

            try:
                shutil.rmtree(output_dir, onerror=on_rm_error)
                print(f"All data in '{output_dir}' has been deleted.")
            except OSError as error:
                print(f"Error deleting data: {error}")
        else:
            print("Data deletion canceled.")
    else:
        print(f"No existing data found in '{output_dir}'.")

def validate_date_input(prompt):
    """Validate user input for a date in YYYY-MM-DD format."""
    while True:
        date_input = input(prompt).strip()
        try:
            return datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid input. Please enter a date in the format YYYY-MM-DD.")

def validate_yes_no_input(prompt):
    """Validate user input for yes/no questions."""
    while True:
        response = input(prompt).strip().lower()
        if response in ['yes', 'no']:
            return response
        print("Invalid input. Please answer 'yes' or 'no'.")

def handle_invalid_input(prompt, valid_choices):
    """
    Validates user input against a set of valid choices.
    If input is invalid, prints an error message and re-prompts the user.
    """
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Invalid input. Please try again.")

def choose_mep(dataframe, column_name):
    """Allow the user to select a specific MEP based on partial matching."""
    while True:
        search_query = input("Enter part of the MEP's name. Press ENTER to list all available MEPs (enter 0 to go back to main menu): ").strip()
        if search_query == '0':
            return None
        matches = dataframe[dataframe[column_name].str.contains(search_query, case=False, na=False)]
        if matches.empty:
            print("No name matched. Try again or enter a different MEP.")
            continue

        print("Matching names:")
        for i, name in enumerate(matches[column_name].unique(), start=1):
            print(f"{i}. {name}")

        while True:
            choice = input("Select the number of the MEP (or 0 to go back): ").strip()
            if choice == '0':
                break

            if choice.isdigit() and 1 <= int(choice) <= len(matches[column_name].unique()):
                selected_name = matches[column_name].unique()[int(choice) - 1]
                return selected_name
            print("Invalid choice. Please select a valid number.")

def retrieve_mep_id(dataframe, selected_mep):
    """
    Retrieve the MEP_ID for the first occurrence where Speaker Name matches the selected MEP.
    """
    match = dataframe[dataframe['Speaker Name'] == selected_mep]
    if not match.empty:
        return match.iloc[0]['MEPID']
    print(f"No matching MEPID found for Speaker Name: {selected_mep}")
    return None

def initialize_output_dir(output_dir):
    """Handle directory initialization and deletion."""
    delete_data = validate_yes_no_input(
        "Do you want to delete all previously downloaded data? "
        "Does not work with third-party cloud servers. (yes/no): "
    )
    if delete_data == 'yes':
        delete_existing_data(output_dir)
    os.makedirs(output_dir, exist_ok=True)

def analyze_speeches(combined_speeches_csv_path, output_dir):
    """Perform speech analysis."""
    if not os.path.exists(combined_speeches_csv_path):
        print("No speech data available. Please download and process speeches first.")
        return

    try:
        df = pd.read_csv(combined_speeches_csv_path)
        analysis_dir = os.path.join(output_dir, "analysis")
        analyze_summary_statistics(df, analysis_dir)

        for file in os.listdir(analysis_dir):
            if file.endswith(".png"):
                img_path = os.path.join(analysis_dir, file)
                plt.figure()
                img = plt.imread(img_path)
                plt.imshow(img)
                plt.axis('off')
        plt.show(block=False)
        print(f"Graphs saved in '{analysis_dir}'. Check the directory for the results.")
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        print(f"An unexpected error occurred: {e}")

def analyze_specific_words_menu(combined_speeches_csv_path):
    """Find and summarize specific speeches by word(s)."""
    if not os.path.exists(combined_speeches_csv_path):
        print("No speech data available. Please process and translate speeches first.")
        return

    try:
        df = pd.read_csv(combined_speeches_csv_path)
        while True:
            words = input("Enter the word(s) to search for, separated by spaces (or press 0 to return): ").strip()
            if words == "0":
                print("Returning to menu.")
                break
            if words:
                analyze_specific_words(df, words)
            else:
                print("No words entered. Please try again.")
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        print(f"An unexpected error occurred: {e}")


def summarize_voting_menu(combined_voting_csv_path):
    """Generate summary statistics for voting data."""
    if not os.path.exists(combined_voting_csv_path):
        print("No voting data available. Please download and process votings first.")
        return

    try:
        df = pd.read_csv(combined_voting_csv_path)
        summarize_voting_statistics(df)
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        print(f"An unexpected error occurred: {e}")

def analyze_summary_statistics_menu(output_dir, combined_speeches_csv_path):
    """
    Generate and display summary statistics of speeches.
    """
    try:
        df = pd.read_csv(combined_speeches_csv_path)
        analysis_dir = os.path.join(output_dir, "analysis")
        analyze_summary_statistics(df, analysis_dir)

        for file in os.listdir(analysis_dir):
            if file.endswith(".png"):
                img_path = os.path.join(analysis_dir, file)
                plt.figure()
                img = plt.imread(img_path)
                plt.imshow(img)
                plt.axis('off')
        plt.show(block=False)
        print(f"Graphs saved in '{analysis_dir}'. Check the directory for the results.")
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        print(f"An error occurred while processing speeches: {e}")

def analyze_comparison_statistics(df, selected_mep, output_dir):
    """Generate comparison statistics for the MEP."""
    analysis_dir = os.path.join(output_dir, "analysis_mep")
    analyze_summary_statistics_with_respect_to_mep(df, selected_mep, analysis_dir)
    for file in os.listdir(analysis_dir):
        if file.endswith(".png"):
            img_path = os.path.join(analysis_dir, file)
            plt.figure()
            img = plt.imread(img_path)
            plt.imshow(img)
            plt.axis('off')
    plt.show(block=False)
    print(f"Graphs saved in '{analysis_dir}'. Check the directory for the results.")

def analyze_specific_words_for_mep(df, selected_mep):
    """Analyze specific words used by the MEP."""
    while True:
        words = input("Enter the word(s) to search for, separated by spaces (or press 0 to return): ").strip()
        if words == "0":
            print("Returning to menu.")
            break
        if words:
            try:
                analyze_specific_words_filtered_by_mep(df, selected_mep, words)
            except (ValueError, KeyError) as e:
                print(f"An unexpected error occurred: {e}")
        else:
            print("No words entered. Please try again.")

def analyze_votings_for_mep(combined_voting_csv_path, df, selected_mep):
    """Analyze voting data for the MEP."""
    if not os.path.exists(combined_voting_csv_path):
        print("No voting data available. Please download and process votings first.")
        return
    try:
        df_voting = pd.read_csv(combined_voting_csv_path)
        selected_mep_id = retrieve_mep_id(df, selected_mep)
        summarize_voting_statistics_mep(df_voting, selected_mep, selected_mep_id)
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError, KeyError) as e:
        print(f"An error occurred while processing voting data: {e}")
