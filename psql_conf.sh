#!/bin/bash
#
# This file contains configuration settings, such as the name of the database
# and the arguments for various PostgreSQL commands.
#

# The name of the PostgreSQL database.
# IMPORTANT: The following line must appear only once and the database name
# must be surrounded by single quotes.
DBNAME='pg_guyton'
# The file that contains the database schema.
SCHEMA='schema.sql'

# The PostgreSQL interactive terminal.
PSQL=$(which psql)
# A wrapper around the 'CREATE DATABASE' SQL command.
CREATEDB=$(which createdb)
# The PostgreSQL backup utility.
PGDUMP=$(which pg_dump)

# Options for all instances of the PostgreSQL interactive terminal.
PG_ARGS='--no-psqlrc --quiet --pset pager=off'
# An additional option for when a single transaction is required.
PG_SINGLE='--single-transaction'
# Setting this variable hides superfluous warnings.
PG_OPTIONS='--client-min-messages=warning'

# Additional arguments for the createdb command.
# For example, to use a custom tablespace:
# CREATE_ARGS='-D tablespacename'
CREATE_ARGS=''

# Options for the PostgreSQL backup utility.
PGDUMP_ARGS='--format=custom --compress=9'

# The exit code to return when an error occurs.
EXIT_ERR=2

# Ensure that the PostgreSQL interactive terminal can be found.
if [ "" = "${PSQL}" ]; then
    echo 'ERROR: unable to find "psql".'
    exit ${EXIT_ERR}
fi

# Ensure that the createdb command can be found.
if [ "" = "${CREATEDB}" ]; then
    echo 'ERROR: unable to find "createdb".'
    exit ${EXIT_ERR}
fi

# Ensure that the backup utility can be found.
if [ "" = "${PGDUMP}" ]; then
    echo 'ERROR: unable to find "pgdump".'
    exit ${EXIT_ERR}
fi
