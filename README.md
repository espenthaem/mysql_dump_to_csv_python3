# MySQL dump to CSV for python3
## Background
A quick and dirty python script to convert the SQL file from a mysqldump to multiple csv files for python3

It is largely based on the mysql_dumpt_to_csv project by the GitHub user jamesmishra. I've added a couple of bits of functionality:

1. The csv files are named according to the table name in the CSV file
2. The headers of the SQL tables are preserved
3. Multiple insert statements are handled correctly


## Usage
Run `python mysqldump_to_csv.py` followed by the filename of the SQL file


## How It Works
Every line is checked for the `'CREATE TABLE'` and `'INSERT INTO' statements.`
If the first statement is observed, the following lines are extracted to obtain the headers of the SQL table.
If the second statement is observed, the rest of the line is converted to CSV.
