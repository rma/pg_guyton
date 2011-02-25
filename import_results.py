#!/usr/bin/python


"""This script imports simulation results into the pg_guyton database.

   USAGE: import_results.py [-t tag -d -p num] results_file

   ARGUMENTS
       results_file:  A file containing the simulation results.

   OPTIONS
       -d, --dry-run
           Perform a dry-run, printing the SQL statements.

       -h, --help
           Display this help message.

       -p NUM, --progress=NUM
           Mark progress after importing every NUM simulations.

       -t TAG, --tag=TAG
           Mark all imported simulations with the tag having the name TAG.
           Multiple tags can be used by passing this option multiple times.

"""

import datetime
import getopt
import os
import psycopg2
import pwd
import subprocess
import sys

from import_parser import par_list, par_of_interest, var_list, var_of_interest, parse

DEBUG = False
"""When set to True, a dry-run is performed where SQL queries are printed, but
   not executed."""

def do_stmt(cursor, stmt, data, retval=False):
    """Executes a single statement for each tuple in data. Return values are
    retrieved when retval is set to True."""
    if DEBUG:
        print stmt, data
        return None
    else:
        try:
            if isinstance(data, tuple):
                cursor.execute(stmt, data)
            elif isinstance(data, list):
                cursor.executemany(stmt, data)
            else:
                print >> sys.stderr, "ERROR: invalid data " + str(data)
                return
            if retval:
                return cursor.fetchall()
        except Exception, e:
            if hasattr(e, 'pgerr'):
                print >> sys.stderr, e.pgerr
            print >> sys.stderr, sys.exc_info()
            print >> sys.stderr, stmt
            print >> sys.stderr, data

def create_experiment(cursor, model_ID):
    """Creates a new experiment and returns the experiment ID."""
    at_time = datetime.datetime.utcnow()
    by_user = pwd.getpwuid(os.getuid())[0]
    on_host = os.uname()[1]

    stmt = ("INSERT INTO experiment (model, at_time, by_user, on_host) "
            "VALUES (%s, %s, %s, %s) RETURNING id")
    data = (model_ID, at_time, by_user, on_host)

    return do_stmt(cursor, stmt, data, retval=True)[0][0]

def save_params(cursor, expID, p_init, param_IDs):
    """Records the initial parameters for a simulation."""
    stmt = ("INSERT INTO param_value "
            "(experiment, parameter, at_time, value, of_interest) "
            "VALUES (%s, %s, %s, %s, %s)")

    p_list = zip(p_init, par_list())
    data_fn = lambda (v,n): (expID, param_IDs[n], 0, v, par_of_interest(n))
    data = map(data_fn, p_list)

    do_stmt(cursor, stmt, data)

def save_delta(cursor, expID, delta_param, delta_incr, param_IDs):
    """Records the delta perturbation for a simulation."""
    paramID = param_IDs[par_list()[delta_param]]
    # the delta perturbation is applied after four weeks
    at_time = 60 * 24 * 7

    stmt = ("SELECT value FROM param_value "
            "WHERE experiment = %s AND parameter = %s AND at_time = %s ")
    data = (expID, paramID, 0)

    matches = do_stmt(cursor, stmt, data, retval=True)
    if len(matches) != 1:
        print >> sys.stderr, "ERROR: " + str(len(matches)) + " initial values"
        return
    else:
        new_val = delta_incr + matches[0][0]
        pname = par_list()[delta_param]

    stmt = ("INSERT INTO param_value "
            "(experiment, parameter, at_time, value, of_interest) "
            "VALUES (%s, %s, %s, %s, %s)")
    of_interest = par_of_interest(pname)
    data = (expID, paramID, at_time, new_val, of_interest)

    do_stmt(cursor, stmt, data)

def save_state(cursor, expID, state, why_now, var_IDs):
    """Records a state from the state history of a simulation."""
    time_index = var_list().index("T")
    time = state[time_index]
    values = state

    varIDs = map(lambda n: var_IDs[n], var_list())
    varIDs_set = set(varIDs)
    if len(varIDs) != len(varIDs_set):
        print >> sys.stderr, "ERROR: non-unique variable IDs"
        return

    stmt = ("INSERT INTO var_value "
            "(experiment, variable, at_time, value, why_now, of_interest) "
            "VALUES (%s, %s, %s, %s, %s, %s)")

    v_list = zip(values, var_list())
    data_fn = lambda (v,n): (expID, var_IDs[n], time, v, why_now,
                             var_of_interest(n))
    data = map(data_fn, v_list)
    do_stmt(cursor, stmt, data)

def save_tags(cursor, expID, tags):
    """Records the tags associated with a simulation."""
    stmt = ("INSERT INTO tagged_with (experiment, tag) "
            "VALUES (%s, %s)")
    data = map(lambda tagID: (expID, tagID), tags.itervalues())

    do_stmt(cursor, stmt, data)

def import_result(settings, init_params, delta_param, delta_incr, pre_delta,
                  post_deltas, count):
    """Creates a new experiment and records the associated simulation data."""
    # Load the settings for the importing process.
    (cursor, conn, model_ID, param_IDs, var_IDs, tag_IDs, log_per) = settings

    # Create a new experiment
    expID = create_experiment(cursor, model_ID)
    # Save the initial parameter values
    save_params(cursor, expID, init_params, param_IDs)
    # Save the delta
    save_delta(cursor, expID, delta_param, delta_incr, param_IDs)
    # Save the state history
    why_now = 1
    for state in [pre_delta] + post_deltas:
        save_state(cursor, expID, state, why_now, var_IDs)
        why_now += 1

    # Tag the simulation
    save_tags(cursor, expID, tag_IDs)

    # Log progress after every X simulations
    if count % log_per == 0:
        print count
        sys.stdout.flush()

def connect_and_import(results_file, tags, host=None, user=None, password=None,
                       log_per=500):
    """Records the simulation results stored in results_file."""
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
        # The default isolation level is READ_COMMITTED, which is perfect
        cursor = conn.cursor()

        # TODO -- allow the model to be specified on the command line
        model_ID = 1

        # Retrieve parameter IDs
        param_IDs = {}
        cursor.execute("SELECT parameter.name, parameter.id "
                       "FROM parameter INNER JOIN defined_for "
                       "ON (defined_for.model = %s)", (model_ID,))
        for (p_name, p_id) in cursor:
            param_IDs[p_name] = p_id

        # Retrieve variable IDs
        var_IDs = {}
        cursor.execute("SELECT name, id FROM variable")
        for (v_name, v_id) in cursor:
            var_IDs[v_name] = v_id

        # Retrieve tag IDs, creating tags where necessary
        tag_IDs = {}
        if 'Perturbation' not in tags:
            tags.append('Perturbation')
        for tag_name in tags:
            cursor.execute("SELECT id FROM tag WHERE name = %s", (tag_name,))
            result = cursor.fetchone()
            if result is None or len(result) < 1:
                print >> sys.stderr, ("Creating tag '%s'" % (tag_name,))
                cursor.execute("INSERT INTO tag (name, description) "
                    "VALUES (%s, %s) RETURNING id", (tag_name, ''))
                tag_id = cursor.fetchone()[0]
            else:
                tag_id = result[0]
            tag_IDs[tag_name] = tag_id

        info = (cursor, conn, model_ID, param_IDs, var_IDs, tag_IDs, log_per)

        with open(results_file) as results:
            count = parse(results, import_result, info, warn=True)

        print count, "simulations were imported."
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
    connect_and_import() in order to record the simulation results."""
    if argv is None:
        argv = sys.argv
    try:
        try:
            o_short = "t:p:dh"
            o_long = ["tag=", "progress=", "debug", "help"]
            opts, args = getopt.getopt(argv[1:], o_short, o_long)
        except getopt.error, msg:
             raise Usage(msg)

        # Default to applying no tags
        tags = []
        # Default to logging progress after every 500 records
        log_per = 500

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 2
            elif o in ("-t", "--tag"):
                tags.append(a)
            elif o in ("-d", "--dry-run"):
                DEBUG = True
            elif o in ("-p", "--progress"):
                log_per = int(a)

        if len(args) != 1:
            print __doc__
            return 2

        connect_and_import(args[0], tags, log_per=log_per)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
