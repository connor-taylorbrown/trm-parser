#!/bin/bash

role="$1"

if [ -z "$role" ]; then
    echo "Usage: $0 <role>"
    echo "Example: $0 V"
    exit 1
fi

echo count,item,construction > merged-$role.csv
for file in *"$role".txt; do
    filename="${file%.*}"
    cat "$file" | tr ' ' , | sed -e "s/$/,$filename/" >> merged-$role.csv
done

cat merged-$role.csv | sort -k 1 -V -r | tee merged-$role.csv
