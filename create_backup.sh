#!/bin/bash
#
# This script creates a backup of the database.
#

source ./psql_conf.sh

if [ "$#" -eq "0" ]; then
    OUT=${DBNAME}.dump
elif [ "$#" -eq "1" ]; then
    OUT="$1"
else
    echo 'USAGE: create_backup.sh [output_file]'
    exit ${EXIT_ERR}
fi

${PGDUMP} --file=${OUT} ${DBNAME}
