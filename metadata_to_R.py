#!/usr/bin/python

"""This script formats the metadata in a suitable form for R.

   USAGE: metadata_to_R.py metadata.txt

"""

import csv
import getopt
import sys

class InvalidLine(Exception):
    """This exception is raised when create_metadata.data_reader encounters a
    line with an invalid number of fields."""
    def __init__(self, msg):
        self.msg = msg

def data_reader(results):
    """The data_reader generator parses blocks of lines that provide metadata
    for model parameters or model variables. It returns tuples that contain
    this parsed data in the following two forms:

    For parameters:
    (name, description, minimum_val, maximum_val, default_val, standard_val)

    For variables:
    (name, description, default_value)

    """
    reader = csv.reader(results, delimiter='\t')
    # parse the results for a single simulation
    for line in reader:
        # find the first non-empty line that doesn't start with '#'
        title = ""
        while len(line) < 1 or line[0][0] == '#':
            if len(line) > 0 and line[0][0] == '#':
                title = line[0][1:]
            line = filter(None, reader.next())
        lines = []
        # read in all lines until the next empty line
        while len(line) > 1:
            try:
                name = line[0].upper()
                if name == 'I' or name == 'T':
                    t_var = (name, line[1], float(line[2].replace("d", "E")))
                    lines.append(t_var)
                elif len(line) == 4:
                    desc = line[3]
                    def_val = float(line[1].replace("d", "E"))
                    t_var = (name, desc, def_val)
                    lines.append(t_var)
                elif len(line) == 6:
                    def_val = float(line[1].replace("d", "E"))
                    std_val = float(line[2].replace("d", "E"))
                    min_val = float(line[3].replace(",", "."))
                    max_val = float(line[4].replace(",", "."))
                    desc = line[5]
                    t_par = (name, desc, min_val, max_val, def_val, std_val)
                    lines.append(t_par)
                else:
                    print len(line)
                    msg = 'Line must have 4 or 6 fields, not %d' % len(line)
                    raise InvalidLine(msg)

                line = filter(None, reader.next())
            except StopIteration as e:
                break
        yield (title, lines)

def format_metadata(data):
    """Populates the metadata for model parameters and variables."""
    writer = csv.writer(sys.stdout, delimiter='\t')

    for title, lines in data_reader(data):
         if title == 'Parameters':
             for (name, desc, min_val, max_val, def_val, std_val) in lines:
                 writer.writerow([name, desc.strip()])
         elif title == 'Variables':
             for (name, desc, def_val) in lines:
                 writer.writerow([name, desc.strip()])

class Usage(Exception):
    """This exception is raised when invalid command-line arguments are given,
    or when the user passes '-h' or '--help' on the command-line."""
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    """The main() function processes the command-line arguments and then calls
    format_metadata() in order to format the metadata."""
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
             raise Usage(msg)

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 2

        if len(args) != 1:
            print __doc__
            return 2

        with open(args[0]) as data:
            format_metadata(data)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

