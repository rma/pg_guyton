#!/bin/sh
#
# Re-create the database and import results from a file.
#

if [ ! "$#" = "1" ]; then
    echo USAGE: `basename $0` '[input_file]' >&2
    exit 1
fi

if [ ! -r $1 ]; then
    echo ERROR: unable to read file "'"$1"'" >&2
    exit 1
fi

source ./psql_conf.sh

dropdb ${DBNAME}
./create_db.sh
./create_metadata.py metadata.txt
./import_results.py $1
