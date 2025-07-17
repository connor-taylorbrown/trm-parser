#!/bin/bash

mbc_context="$1"; shift

for var in "$@"; do
    if [ "$1" = "-v" ]; then
        if [[ $mbc_context = *det-TA ]]; then
            echo $mbc_context $role - ASV
        else
            echo $mbc_context $role - AVS
        fi
    fi

    if [ "$1" = "-h" ]; then
        echo "Usage: $0 <mbc_context> <role> [-v] [-h] [-o]"
        echo "Example: $0 ma-det-TA S -v"
        exit 0
    fi

    if [ "$1" = "-b" ]; then
        mkdir -p output/bases
        base=true
    fi

    if [ "$1" = "-c" ]; then
        mkdir -p output/counts
        shift
        role="$1"
    fi

    shift
done

filter_lines() {
    if [ $role = "S" ]; then
        grep -w AE | grep -vw VS | grep -vw covert
    else
        grep -w AE
    fi
}

select_columns() {
    if [ $role = "S" ]; then
        if [[ $mbc_context = *det-TA ]]; then
            awk -F',' '{print $4}'
        else
            awk -F',' '{print $5}'
        fi
    elif [ $role = "V" ]; then
        if [[ $mbc_context = *det-TA ]]; then
            awk -F',' '{print $5}'
        else
            awk -F',' '{print $4}'
        fi
    elif [ $role = "A" ]; then
        awk -F',' '{print $3}'
    else
        echo "Invalid role: $role"
        exit 1
    fi
}

if [ -n "$base" ]; then
    cat output/context/$mbc_context.txt | \
    filter_lines | \
    ./base.sh $mbc_context | \
    tee output/bases/$mbc_context.txt
elif [ -n "$role" ]; then
    cat output/bases/$mbc_context.txt | \
    tr ' ' , | \
    select_columns | \
    sort | \
    uniq -c | \
    sed -e 's/^ *//' | \
    sort -k 1 -V -r |\
    tee output/counts/$mbc_context-$role.txt
else
    echo "No operation specified. Use -b for base or -c for count."
    exit 1
fi
