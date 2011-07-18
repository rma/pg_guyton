#!/usr/bin/python

"""This script exports simulation results into comma-separated form, suitable
for importing into R.

   USAGE: convert_for_R.py [-o file -t n] results_file

   ARGUMENTS
       results_file:  A file containing the simulation results.

   OPTIONS
       -h, --help
           Display this help message.

       -o FILE, --output=FILE
           Write the output to FILE (default is 'results.csv').

       -t N, --time=N
           Output the state at the Nth time interval, where 1 <= N <= 5.
           The default is N = 5 (ie, the steady-state).

"""

import csv
import getopt
import sys

from import_parser import par_list, par_of_interest, var_list, var_of_interest, parse, delta_index

def convert(settings, params, del_param, del_incr, pre_del, post_dels, count):
    """Converts the results of a simulation into comma-separated form."""
    (writer, p_interest, v_interest, nth_time) = settings

    # Save the original steady-state
    params = params[0:p_interest]
    output = pre_del[0:v_interest]
    writer.writerow(params + output)

    # Save the post-delta steady-state
    del_idx = delta_index(del_param)
    params[del_idx] += del_incr
    delta_output = post_dels[nth_time][0:v_interest]
    writer.writerow(params + delta_output)

class Usage(Exception):
    """This exception is raised when invalid command-line arguments are given,
    or when the user passes '-h' or '--help' on the command-line."""
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    """The main() function processes the command-line arguments and then
    converts the simulation results."""
    if argv is None:
        argv = sys.argv
    try:
        try:
            o_short = "o:t:h"
            o_long = ["output=", "time=", "help"]
            opts, args = getopt.getopt(argv[1:], o_short, o_long)
        except getopt.error, msg:
             raise Usage(msg)

        # The default output file.
        out_file = 'results.csv'
        # Which snapshot to record.
        nth_time = 4

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 2
            elif o in ("-o", "--output"):
                out_file = a
            elif o in ("-t", "--time"):
                nth_time = int(a) - 1

        if len(args) != 1 or nth_time < 0 or nth_time > 4:
            print __doc__
            return 2

        p_interest = par_list().index('VV9') + 1
        v_interest = var_list().index('GFR') + 1

        p_name = lambda n: "p_" + n
        v_name = lambda n: "v_" + n
        p_names = map(p_name, par_list()[0:p_interest])
        v_names = map(v_name, var_list()[0:v_interest])

        with open(out_file, 'wb') as output:
            writer = csv.writer(output, delimiter=',')
            writer.writerow(p_names + v_names)

            settings = (writer, p_interest, v_interest, nth_time)
            with open(args[0]) as results:
                count = parse(results, convert, settings, warn=True)

        print count, "simulations were converted."

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

