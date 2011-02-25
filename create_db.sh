#!/bin/bash
#
# This script creates the (empty) database, according to the schema.
#

source ./psql_conf.sh

if ${CREATEDB} ${CREATE_ARGS} ${DBNAME}; then
    ${PSQL} ${PG_ARGS} --dbname ${DBNAME} --file ${SCHEMA}
else
    echo 'ERROR: could not create the database.'
    exit ${EXIT_ERR}
fi
