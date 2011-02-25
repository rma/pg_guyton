#!/usr/bin/python

"""This script populates the database with parameter and variable metadata.

   USAGE: create_metadata.py metadata.txt

"""

import csv
import getopt
import psycopg2
import subprocess
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

def populate_data(data, cursor, model_ID):
    """Populates the metadata for model parameters and variables."""
    for title, lines in data_reader(data):
         if title == 'Parameters':
             for (name, desc, min_val, max_val, def_val, std_val) in lines:
                 cursor.execute("INSERT INTO parameter "
                   "(name, units, description, min_val, max_val, default_val) "
                   "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                   (name, '', desc, min_val, max_val, def_val))
                 param_ID = cursor.fetchone()[0]
                 cursor.execute("INSERT INTO defined_for (model, parameter) "
                     "VALUES (%s, %s)", (model_ID, param_ID))
         elif title == 'Other Parameters':
             for (name, desc, def_val) in lines:
                 cursor.execute("INSERT INTO parameter "
                   "(name, units, description, min_val, max_val, default_val) "
                   "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                   (name, '', desc, float('nan'), float('nan'), def_val))
                 param_ID = cursor.fetchone()[0]
                 cursor.execute("INSERT INTO defined_for (model, parameter) "
                     "VALUES (%s, %s)", (model_ID, param_ID))
         elif title == 'Variables':
             for (name, desc, def_val) in lines:
                 cursor.execute("INSERT INTO variable "
                   "(name, units, description, default_val) "
                   "VALUES (%s, %s, %s, %s) RETURNING id",
                   (name, '', desc, def_val))
         elif title == 'Other Variables':
             for (name, desc, def_val) in lines:
                 cursor.execute("INSERT INTO variable "
                   "(name, units, description, default_val) "
                   "VALUES (%s, %s, %s, %s) RETURNING id",
                   (name, '', desc, def_val))

TAGS = [
    ('Perturbation', 'An experiment with a perturbation in one parameter.'),
]

def populate_tags(cursor):
    """Populates the default tags (TAGS)."""
    for (tag, desc) in TAGS:
        cursor.execute("INSERT INTO tag (name, description) VALUES (%s, %s)",
            (tag, desc))

MODELS = [
    ('Guyton92', 'The 1992 Guyton model', 'No publication'),
]

def populate_models(cursor):
    """Populates the default models (MODELS)."""
    model_IDs = []
    for (name, desc, ref) in MODELS:
        cursor.execute("INSERT INTO model (name, description, reference) "
            "VALUES (%s, %s, %s) RETURNING id", (name, desc, ref))
        model_IDs.append( cursor.fetchone()[0] )
    return model_IDs

DETAILS = [
    ('Pre-delta', 'The steady-state before the parameter perturbation'),
    ('5 minutes', 'Five minutes after the parameter perturbation'),
    ('1 hour', 'One hour after the parameter perturbation'),
    ('1 day', 'One day after the parameter perturbation'),
    ('1 week', 'One week after the parameter perturbation'),
    ('4 weeks', 'Four weeks after the parameter perturbation'),
]

def populate_time_details(cursor):
    """Populates the default time_details (DETAILS)."""
    for (name, desc) in DETAILS:
        cursor.execute("INSERT INTO time_detail (name, description) "
            "VALUES (%s, %s)", (name, desc))

def connect_and_populate(data_file, host=None, user=None, password=None):
    """This function connects to the database and then populates various
    metadata, from details of model parameters and variables (stored in the
    data_file file) to default models, experiment tags and time_details."""
    # Extract the database name from psql_conf.sh (this bit isn't pretty)
    p = subprocess.Popen(
        "grep '^DBNAME=' psql_conf.sh | sed 's/DBNAME/dbname/'",
        shell=True, stdout=subprocess.PIPE)
    conn_strs = map(lambda s: s.strip(), p.stdout.readlines())

    if host is not None:
        conn_strs.append("host='%s'" % (host,))
    if user is not None:
        conn_strs.append("user='%s'" % (user,))
    if password is not None:
        conn_strs.append("password='%s'" % (password,))
    conn_string = " ".join(conn_strs)

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        model_IDs = populate_models(cursor)
        populate_time_details(cursor)
        with open(data_file) as data:
            populate_data(data, cursor, model_IDs[0])
        populate_tags(cursor)
        conn.commit()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("%s" % (exceptionValue))
    finally:
        if locals().has_key('conn'):
            conn.close()

class Usage(Exception):
    """This exception is raised when invalid command-line arguments are given,
    or when the user passes '-h' or '--help' on the command-line."""
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    """The main() function processes the command-line arguments and then calls
    connect_and_populate() in order to populate the database with metadata."""
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

        connect_and_populate(args[0])
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
