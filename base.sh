#!/bin/bash

mbc_context="$1"; shift
input_file="/dev/stdin"

source output/context/queries.sh $mbc_context

if [ -z "$query" ]; then
    echo "Error: 'query' variable is not set for $mbc_context." >&2
    exit 1
fi

test_line() {
    local context="$1"
    local i="$2"
    local tag="$3"

    doc=$(echo "$context" | awk '{print $1}')
    line_num=$(echo "$context" | awk '{print $2}')
    while IFS= read -r output_line; do
        if [[ $i -eq 0 ]]; then
            echo "$output_line"
        fi
        ((i--))
    done < <(python3 -m sentence.query -d $doc -g $line_num $query)
}

context=0
i=0
while IFS= read -r line; do
    if [[ ! "$line" =~ ^[0-9]+ ]]; then
        continue
    fi
    
    n=$(echo "$line" | awk '{print $1, $2}')
    if [[ "$n" != "$context" ]]; then
        context="$n"
        i=0
    fi

    test_line "$context" "$i" "$(echo "$line" | awk '{print $3}')"
    ((i++))
done < "$input_file"