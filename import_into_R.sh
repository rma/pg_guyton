#!/bin/sh

BASE="virtppl"
EXT="csv"

TIMES="1m 1h 1d 1w 4w"

if [ "$#" != 1 ]; then
    echo USAGE: import_into_R.sh results_file
    exit 2
fi

if [ ! -r "$1" ]; then
    echo ERROR: unable to read file \'$1\'
    exit 2
fi

COUNT=1

for T in ${TIMES}; do
    OUTFILE=${BASE}.${T}.${EXT}
    echo ./convert_for_R.py -o ${OUTFILE} -t ${COUNT} $1
    ./convert_for_R.py -o ${OUTFILE} -t ${COUNT} $1
    COUNT=$(( ${COUNT} + 1 ))
done

R --no-save < ./import_into_R.R
