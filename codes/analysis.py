"""
Module for analyzing and visualizing MEP speech and voting data.
"""
import os
import re
import matplotlib.pyplot as plt

def plot_histogram(data, title, xlabel, output_file=None, highlight_value=None):
    """
    Create and save a histogram with an optional highlight line for a specific value.
    """
    plt.figure(figsize=(10, 6))
    data_filtered = data.dropna()
    lower_bound, upper_bound = data_filtered.quantile(0.05), data_filtered.quantile(0.95)
    data_filtered = data_filtered[(data_filtered >= lower_bound) & (data_filtered <= upper_bound)]

    plt.hist(data_filtered, bins=30, edgecolor='black', alpha=0.7)
    mean_value = data.mean()
    plt.axvline(mean_value, color='black', linestyle='--', linewidth=1.5, label=f"Mean: {mean_value:.2f}")
    if highlight_value is not None:
        plt.axvline(highlight_value, color='red', linestyle='-', linewidth=1.5,
                    label=f"Selected MEP: {highlight_value:.2f}")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    if output_file:
        plt.savefig(output_file)
    plt.close()

def analyze_speech_counts(dataframe, output_file=None, highlight_value=None):
    """
    Analyze and plot the distribution of number of speeches by MEPs.
    """
    speech_counts = dataframe.groupby('Speaker Name')['Text'].count()
    plot_histogram(speech_counts, "Distribution of Number of Speeches by MEPs",
                   "Number of Speeches", output_file, highlight_value)

def analyze_total_speech_time(dataframe, output_file=None, highlight_value=None):
    """
    Analyze and plot the distribution of total speech times by MEPs.
    """
    total_speech_time = dataframe.groupby('Speaker Name')['Duration'].sum()
    plot_histogram(total_speech_time, "Distribution of Total Speech Time by MEPs",
                   "Total Speech Time (seconds)", output_file, highlight_value)

def analyze_avg_speech_time(dataframe, output_file=None, highlight_value=None):
    """
    Analyze and plot the distribution of average speech times by MEPs.
    """
    avg_speech_time = dataframe.groupby('Speaker Name')['Duration'].mean()
    plot_histogram(avg_speech_time, "Distribution of Average Speech Time by MEPs",
                   "Average Speech Time (seconds)", output_file, highlight_value)

def analyze_avg_speech_length(dataframe, output_file=None, highlight_value=None):
    """
    Analyze and plot the distribution of average speech lengths (in words) by MEPs.
    """
    dataframe['Speech Length'] = dataframe['Text'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

    avg_speech_length = dataframe.groupby('Speaker Name')['Speech Length'].mean()
    plot_histogram(avg_speech_length, "Distribution of Average Speech Length by MEPs",
                   "Average Speech Length (words)", output_file, highlight_value)

def analyze_summary_statistics(dataframe, output_dir):
    """
    Generate and save summary statistics graphs for all speeches.
    """
    os.makedirs(output_dir, exist_ok=True)

    analyze_speech_counts(dataframe, output_file=os.path.join(output_dir, "speech_count_distribution.png"))
    analyze_total_speech_time(dataframe, output_file=os.path.join(output_dir, "total_speech_time_distribution.png"))
    analyze_avg_speech_time(dataframe, output_file=os.path.join(output_dir, "avg_speech_time_distribution.png"))
    analyze_avg_speech_length(dataframe, output_file=os.path.join(output_dir, "avg_speech_length_distribution.png"))

def analyze_summary_statistics_with_respect_to_mep(dataframe, mep_name, output_dir):
    """
    Generate and save summary statistics graphs for all speeches with respect to a specific MEP.
    """
    os.makedirs(output_dir, exist_ok=True)

    speech_counts = dataframe.groupby('Speaker Name')['Text'].count()
    analyze_speech_counts(dataframe,
                          output_file=os.path.join(output_dir, "speech_count_with_mep.png"),
                          highlight_value=speech_counts.get(mep_name, None))

    total_speech_time = dataframe.groupby('Speaker Name')['Duration'].sum()
    analyze_total_speech_time(dataframe,
                              output_file=os.path.join(output_dir, "total_speech_time_with_mep.png"),
                              highlight_value=total_speech_time.get(mep_name, None))

    avg_speech_time = dataframe.groupby('Speaker Name')['Duration'].mean()
    analyze_avg_speech_time(dataframe,
                            output_file=os.path.join(output_dir, "avg_speech_time_with_mep.png"),
                            highlight_value=avg_speech_time.get(mep_name, None))

    dataframe['Speech Length'] = dataframe['Text'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)
    avg_speech_length = dataframe.groupby('Speaker Name')['Speech Length'].mean()
    analyze_avg_speech_length(dataframe,
                              output_file=os.path.join(output_dir, "avg_speech_length_with_mep.png"),
                              highlight_value=avg_speech_length.get(mep_name, None))

def summarize_specific_mep(dataframe, mep_name):
    """
    Print summary statistics for a specific MEP.
    """
    dataframe['Speech Length'] = dataframe['Text'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

    mep_data = dataframe[dataframe['Speaker Name'] == mep_name]

    total_speeches = mep_data.shape[0]
    total_time = mep_data['Duration'].sum()
    avg_time = mep_data['Duration'].mean()
    avg_length = mep_data['Speech Length'].mean()

    print(f"\nSummary Statistics for {mep_name}:")
    print(f"Total number of speeches: {total_speeches}")
    print(f"Total time of speeches: {total_time:.2f} seconds")
    print(f"Average time of speech: {avg_time:.2f} seconds")
    print(f"Average length of speech: {avg_length:.2f} words")

def analyze_specific_words(dataframe, words):
    """
    Analyze and count the occurrence of specific word(s) in the translated speeches.
    """
    def show_filtered_speeches(filtered_df):
        """
        Display filtered speeches and provide options to view specific speeches.
        """
        print("\nFiltered speeches:")
        print(filtered_df[['Speaker Name', 'Translated Text']])

        while True:
            print("\nWhat do you want to do next?")
            print("1. Select and show text of specific speech")
            print("0. Return")
            sub_choice = input("Enter your choice: ").strip()

            if sub_choice == "1":
                speech_id = input("Enter the ID of the speech you want to see: ").strip()
                if speech_id.isdigit() and int(speech_id) in filtered_df.index:
                    full_speech = filtered_df.loc[int(speech_id), 'Translated Text']
                    print(f"\nSpeech ID {speech_id}:")
                    print(full_speech)
                else:
                    print("Invalid ID. Please try again.")
            elif sub_choice == "0":
                break
            else:
                print("Invalid choice. Please select again.")
    if isinstance(words, str):
        words = [words]
    if 'Translated Text' not in dataframe.columns:
        print("The column 'Translated Text' does not exist in the data. Please ensure translations are processed.")
        return

    filtered_df = dataframe[dataframe['Translated Text'].str.contains('|'.join(words), case=False, na=False)]
    total_occurrences = filtered_df['Translated Text'].str.count('|'.join(words), flags=re.IGNORECASE).sum()

    if total_occurrences == 0:
        print(f"The word(s) {' '.join(words)} do not occur in the speeches. Select another or press 0 for return.")
        return
    print(f"Total occurrences of {' '.join(words)}: {int(total_occurrences)}")

    while True:
        print("\nWhat do you want to do next?")
        print("1. Show all filtered speeches")
        print("0. Return")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_filtered_speeches(filtered_df)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please select again.")

def analyze_specific_words_filtered_by_mep(dataframe, mep, words):
    """
    Analyze and count the occurrence of specific word(s) in the translated speeches for a specific MEP.
    """
    def show_filtered_speeches(filtered_df):
        """
        Display filtered speeches and provide options to view specific speeches.
        """
        print("\nFiltered speeches:")
        print(filtered_df[['Speaker Name', 'Translated Text']])

        while True:
            print("\nWhat do you want to do next?")
            print("1. Select and show text of specific speech")
            print("0. Return")
            sub_choice = input("Enter your choice: ").strip()

            if sub_choice == "1":
                speech_id = input("Enter the ID of the speech you want to see: ").strip()
                if speech_id.isdigit() and int(speech_id) in filtered_df.index:
                    full_speech = filtered_df.loc[int(speech_id), 'Translated Text']
                    print(f"\nSpeech ID {speech_id}:")
                    print(full_speech)
                else:
                    print("Invalid ID. Please try again.")
            elif sub_choice == "0":
                break
            else:
                print("Invalid choice. Please select again.")

    if isinstance(words, str):
        words = [words]

    if 'Translated Text' not in dataframe.columns:
        print("The column 'Translated Text' does not exist in the data. Please ensure translations are processed.")
        return

    mep_filtered_df = dataframe[dataframe['Speaker Name'].str.contains(mep, case=False, na=False)]

    if mep_filtered_df.empty:
        print(f"No speeches found for MEP: {mep}. Returning to menu.")
        return

    filtered_df = mep_filtered_df[mep_filtered_df['Translated Text'].str.contains('|'.join(words), case=False, na=False)]
    total_occurrences = filtered_df['Translated Text'].str.count('|'.join(words), flags=re.IGNORECASE).sum()

    if total_occurrences == 0:
        print(f"The word(s) {' '.join(words)} do not occur in speeches by {mep}. Select another or press 0 for return.")
        return

    print(f"Total occurrences of {' '.join(words)} in speeches by {mep}: {int(total_occurrences)}")

    while True:
        print("\nWhat do you want to do next?")
        print("1. Show all filtered speeches")
        print("0. Return")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_filtered_speeches(filtered_df)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please select again.")

def summarize_voting_statistics(dataframe):
    """
    Create summary statistics for voting data aggregated by unique voting descriptions.
    """
    grouped = dataframe.groupby('Description')['Vote'].value_counts().unstack(fill_value=0)

    grouped = grouped.reindex(columns=['For', 'Against', 'Abstention'], fill_value=0)

    grouped['Outcome'] = grouped.apply(
        lambda row: 'Accepted' if row['For'] > (row['Against'] + row['Abstention']) else 'Rejected', axis=1
    )

    total_votings = grouped.shape[0]

    accepted_votings = grouped[grouped['Outcome'] == 'Accepted'].shape[0]
    rejected_votings = grouped[grouped['Outcome'] == 'Rejected'].shape[0]

    print("\nSummary Statistics for Voting Data:")
    print(f"Total number of votings: {total_votings}")
    print(f"Votings accepted: {accepted_votings}")
    print(f"Votings rejected: {rejected_votings}")

def summarize_voting_statistics_mep(dataframe, selected_mep, selected_mep_id):
    """
    Create summary statistics for a specific MEP based on their votings.
    """
    grouped = dataframe.groupby('Description')['Vote'].value_counts().unstack(fill_value=0)
    total_votings = grouped.shape[0]
    mep_data = dataframe[dataframe['MEP_ID'] == selected_mep_id]

    if mep_data.empty:
        print(f"No voting data found for {selected_mep}.")
        return

    total_votes = mep_data.shape[0]
    votes_for = mep_data[mep_data['Vote'] == 'For'].shape[0]
    votes_against = mep_data[mep_data['Vote'] == 'Against'].shape[0]
    votes_abstain = mep_data[mep_data['Vote'] == 'Abstention'].shape[0]
    absenteeism = total_votings - total_votes

    print(f"\nSummary Statistics for {selected_mep}:")
    print(f"Total number of votes: {total_votes}")
    print(f"Votes For: {votes_for}")
    print(f"Votes Against: {votes_against}")
    print(f"Votes Abstain: {votes_abstain}")
    print(f"Number of absences from voting: {absenteeism}")
