"""
Main module running the program.
"""

import os
import pandas as pd
from codes.analysis import summarize_specific_mep
from codes.speech import download_speeches, parse_speeches, translate_text_file
from codes.voting import download_votings, parse_votings
from codes.helpfunc import (
    delete_existing_data, validate_date_input, validate_yes_no_input,
    choose_mep, handle_invalid_input, analyze_speeches,
    analyze_specific_words_menu, summarize_voting_menu, analyze_comparison_statistics,
    analyze_specific_words_for_mep, analyze_votings_for_mep
)

def analyze_menu(output_dir, combined_speeches_csv_path, combined_voting_csv_path):
    """Display the main menu for analysis options."""
    while True:
        print("\nMain menu:")
        print("1. Summary statistics of speeches")
        print("2. Find and summarize specific speech by word(s). (translation required)")
        print("3. Summary statistics of votings")
        print("4. Analyze specific MEP (speech data needed)")
        print("0. Exit")

        choice = handle_invalid_input("Enter your choice (number): ", ["1", "2", "3", "4", "0"])

        if choice == "1":
            print("Generating summary statistics of speeches.")
            analyze_speeches(combined_speeches_csv_path, output_dir)
        elif choice == "2":
            analyze_specific_words_menu(combined_speeches_csv_path)
        elif choice == "3":
            summarize_voting_menu(combined_voting_csv_path)
        elif choice == "4":
            analyze_mep_menu(combined_speeches_csv_path, combined_voting_csv_path, output_dir)
        elif choice == "0":
            print("Exiting the program. Goodbye!")
            break

def analyze_mep_menu(combined_speeches_csv_path, combined_voting_csv_path, output_dir):
    """Analyze a specific MEP's data."""
    print("Analyze specific MEP...")

    if not os.path.exists(combined_speeches_csv_path):
        print("No speech data available. Please process speeches first.")
        return
    df = pd.read_csv(combined_speeches_csv_path)
    while True:
        selected_mep = choose_mep(df, "Speaker Name")
        if selected_mep is None:
            break
        sub_choice = analyze_mep_submenu(selected_mep, df, combined_voting_csv_path, output_dir)
        if sub_choice == "0":
            break

def analyze_mep_submenu(selected_mep, df, combined_voting_csv_path, output_dir):
    """Display submenu for MEP analysis options."""
    while True:
        print("\nWhat do you want to analyze for MEP:", selected_mep)
        print("1. Summary statistics of specific MEP's speeches.")
        print("2. Summary statistics of specific MEP's speeches with respect to others.")
        print("3. Summary statistics of specific word(s) used in speeches. (translation required)")
        print("4. Summary statistics of specific MEP's votings.")
        print("0. Back")

        sub_choice = handle_invalid_input("Enter your choice (number): ", ["1", "2", "3", "4", "0"])

        if sub_choice == "1":
            print(f"Generating summary statistics for {selected_mep}...")
            summarize_specific_mep(df, selected_mep)
        elif sub_choice == "2":
            print(f"Generating comparison statistics for {selected_mep}...")
            analyze_comparison_statistics(df, selected_mep, output_dir)
        elif sub_choice == "3":
            print(f"Analyzing specific word(s) for {selected_mep}...")
            analyze_specific_words_for_mep(df, selected_mep)
        elif sub_choice == "4":
            print(f"Analyzing votings for {selected_mep}...")
            analyze_votings_for_mep(combined_voting_csv_path, df, selected_mep)
        elif sub_choice == "0":
            return "0"


def main():
    """
    Main function running the program.
    """
    print("Welcome to the MoniMEPs program, monitor MEPs activity!")

    # Step 1: Choose output directory
    output_dir = input("Enter the output directory where the data will be downloaded and saved: ").strip()

    # Step 2: Ask if the user wants to delete all downloaded data
    delete_data = validate_yes_no_input(
        "Do you want to delete all previously downloaded data? This will not work with third-party cloud servers. (yes/no): "
    )
    if delete_data == 'yes':
        delete_existing_data(output_dir)

    # Ensure output directory exists after potential deletion
    os.makedirs(output_dir, exist_ok=True)

    # Step 3: Enter date range (used for both speeches and voting data)
    start_date = validate_date_input("Enter the start date (YYYY-MM-DD): ")
    end_date = validate_date_input("Enter the end date (YYYY-MM-DD): ")

    # Initialize file paths
    combined_speeches_csv_path = os.path.join(output_dir, "combined_speeches.csv")
    combined_voting_csv_path = os.path.join(output_dir, "combined_votings.csv")

    # Step 4: Process speeches
    if validate_yes_no_input("Do you want to download and process speeches? (yes/no): ") == 'yes':
        download_speeches(output_dir, start_date, end_date)
        speeches_dir = os.path.join(output_dir, "speeches")
        parse_speeches(speeches_dir, combined_speeches_csv_path)

        if validate_yes_no_input("Do you want to translate the speeches to English? Note that this can take up to an hour depending on the size of the data. (yes/no): ") == 'yes':
            translate_text_file(combined_speeches_csv_path, combined_speeches_csv_path)

    # Step 5: Process voting data
    if validate_yes_no_input("Do you want to download and process voting data? (yes/no): ") == 'yes':
        download_votings(output_dir, start_date, end_date)
        voting_dir = os.path.join(output_dir, "voting")
        parse_votings(voting_dir, combined_voting_csv_path)

    # Step 6: Analysis menu
    analyze_menu(output_dir, combined_speeches_csv_path, combined_voting_csv_path)



if __name__ == "__main__":
    main()
