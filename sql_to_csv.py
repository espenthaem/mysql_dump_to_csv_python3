#!/usr/bin/env python
import csv
import sys

# This prevents prematurely closed pipes from raising
# an exception in Python
# allow large content in the dump
csv.field_size_limit(100000)

def is_insert(line):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('INSERT INTO') or False

def is_create(line):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('CREATE TABLE') or False

def get_values(line):
    """
    Returns the portion of an INSERT statement containing values
    """
    return line.partition('` VALUES ')[2]

def get_name(line):
    """
    Return the name of the tables
    """
    dummy = line.partition('`')[2]
    return dummy.partition('`')[0]

def get_headers(headerlines):
    """
    Return the header of the tables
    """
    headers = []
    for headerline in headerlines:
        dummy = headerline.partition('`')[2]
        headers.append(dummy.partition('`')[0])
    return headers

def values_sanity_check(values):
    """
    Ensures that values from the INSERT statement meet basic checks.
    """
    assert values
    assert values[0] == '('
    # Assertions have not been raised
    return True


def parse_values(values, tablename, check,headerdict):
    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file
    """
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
    )
    if check[tablename] == 0:
        outfile = open(tablename+".csv",'w',encoding='utf-8',newline='')
    else:
        outfile = open(tablename+".csv",'a',encoding='utf-8',newline='')

    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    # Add the headers if the table is new
    if check[tablename] == 0:
        writer.writerow(headerdict[tablename])

    for reader_row in reader:
        for column in reader_row:
            # If our current string is empty...
            if len(column) == 0 or column == 'NULL':
                latest_row.append("")
                continue
            # If our string starts with an open paren
            if column[0] == "(":
                # Assume that this column does not begin
                # a new row.
                new_row = False
                # If we've been filling out a row
                if len(latest_row) > 0:
                    # Check if the previous entry ended in
                    # a close paren. If so, the row we've
                    # been filling out has been COMPLETED
                    # as:
                    #    1) the previous entry ended in a )
                    #    2) the current entry starts with a (
                    if latest_row[-1][-1] == ")":
                        # Remove the close paren.
                        latest_row[-1] = latest_row[-1][:-1]
                        new_row = True
                # If we've found a new row, write it out
                # and begin our new one
                if new_row:
                    writer.writerow(latest_row)
                    latest_row = []
                # If we're beginning a new row, eliminate the
                # opening parentheses.
                if len(latest_row) == 0:
                    column = column[1:]
            # Add our column to the row we're working on.
            latest_row.append(column)
        # At the end of an INSERT statement, we'll
        # have the semicolon.
        # Make sure to remove the semicolon and
        # the close paren.
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            writer.writerow(latest_row)


def main():
    """
    Parse arguments and start the program
    """
    # Iterate over all lines in all files
    # listed in sys.argv[1:]
    # or stdin if no args given.
    try:
        arg1 = sys.argv[1]
    except IndexError:
        print("Usage: sql_to_csv.py <input filename>")

    # Add a dict to check if a tablename has appeared
    # before
    #check = {"procedure":0,"company":0,"company_member":0,"user_transaction":0,"user":0,"sharetransfer":0,"region":0,"package":0,"survey": 0}
    check = {}
    # Initialize an array to store the headerlines
    headerlines = []
    # Initialize the dict that contains the arrays of headers for every table
    headerdict = {}

    getHeadersLines = False
    line_counter = 0

    infile = open(arg1,'r',encoding='utf-8')
    for line in infile:
        # Check if lines have to be collected for extraction of the headers
        if getHeadersLines:
            if line.startswith('  `'):
                 headerlines.append(line)
            else:
                 headers = get_headers(headerlines)
                 print(headers)
                 headerdict[headername] = headers
                 headerlines = []
                 headers = []
                 getHeadersLines = False
         # Look for a CREATE statement and parse it for the headers
        if is_create(line):
            headername = get_name(line)
            getHeadersLines = True

        # Look for an INSERT statement and parse it.
        if is_insert(line):
            values = get_values(line)
            tablename = get_name(line)
            if tablename not in check:
                check[tablename] = 0
            if values_sanity_check(values) and tablename in check.keys():
                parse_values(values, tablename, check,headerdict)
                check[tablename] += 1
        line_counter += 1

    print(check)
    #except KeyboardInterrupt:
    #    sys.exit(0)
if __name__ == "__main__":
    main()
