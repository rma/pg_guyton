#!/bin/sh
#
# Given a parameter or variable name, this script searches the available
# metadata for the associated description and units.
#

if [ "$#" != "1" ]; then
    echo "USAGE: `basename $0` PARAMETER_NAME"
    echo "       `basename $0` VARIABLE_NAME"
    exit 2
fi

grep -i '^'$1 metadata.txt
