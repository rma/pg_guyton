#!/bin/bash
#
# This script creates a privileged role for the database.
#

source ./psql_conf.sh

if [ "$#" -ne "1" ]; then
    echo 'USAGE: create_role.sh role_name'
    exit 2
fi

PGROLE="$1"

${PSQL} ${PG_ARGS} ${PG_SINGLE} --dbname ${DBNAME} << EOF
    -- create the role
    CREATE ROLE ${PGROLE};
    -- grant privileges on all tables
    SELECT 'GRANT ALL ON '||schemaname||'.'||tablename||' TO ${PGROLE};'
        FROM pg_tables WHERE schemaname = 'public' order by tablename;
EOF
