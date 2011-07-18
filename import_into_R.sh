#!/bin/sh

BASE="virtppl"
EXT="csv"

TIMES="1m 1h 1d 1w 4w"

if [ "$#" != 2 ]; then
    echo USAGE: import_into_R.sh tag results_file
    exit 2
fi

if [ ! -r "$2" ]; then
    echo ERROR: unable to read file \'$2\'
    exit 2
fi

COUNT=1

for T in ${TIMES}; do
    OUTFILE=${BASE}.$1.${T}.${EXT}
    echo ./convert_for_R.py -o ${OUTFILE} -t ${COUNT} $2
    ./convert_for_R.py -o ${OUTFILE} -t ${COUNT} $2
    COUNT=$(( ${COUNT} + 1 ))
done

# R --no-save < ./import_into_R.R
