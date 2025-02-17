# MoniMEPs Program

Program to monitor acitivity of Members of the European Parliament. It monitors their activity during the plenary sessions - their speeches and votings.

To run the program, execute **python main.py** in your console and follow the instructions.

The program works only for data starting from 02/07/2019, when the European Parliament began saving speech transcripts and voting records as XML data.

After selecting your desired output file location (by inserting file directory), and start and end dates for the period you want to download and analyze data from, the program will perform the following tasks:

* Download and parse speech data, with an optional feature to translate them into English.
* Download and parse voting data at the individual level.

All these data will be saved in your chosen directory, where you can access and analyze them more deeply yourself.

**To download and analyze data from a different period, you must restart the program and delete all files in your selected directory!**

### Analysis

The program provides basic data analysis, primarily descriptive, as you follow the instructions.

## Necessary dependencies
All necessary dependencies are listed in *requirements.txt*. You can install them using the command:
**pip install -r requirements1.txt** in your console.

## Tests
To run all the tests, execute **pytest test_main.py** in your console.

# Structure
*test* directory contains all necessary files needed for testing, *codes* directory contains all supportive modules for main.py file.