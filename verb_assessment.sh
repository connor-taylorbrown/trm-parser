#!/bin/bash

for var in "$@"; do
    if [ "$1" = "-q" ]; then shift;
        query="$1"
        echo $query
    fi

    if [ "$1" = "-b" ]; then shift;
        base="$1"
        echo $base
    fi

    shift
done

if [[ $query = "ka" ]]; then
    python3 -m sentence.query -e 1 -f +preposition-determiner -T | grep -iw ka | tee output/results/ka-S.txt

    python3 -m sentence.query -e 2 -f +preposition-determiner-pause -f +determiner-preposition -T | grep -iw ka | tee output/results/ka-S.txt
    python3 -m sentence.query -e 2 -f +preposition-determiner-pause -f +determiner+preposition-past -T | grep -iw ka | grep -iw e | tee output/results/ka-e.txt
    python3 -m sentence.query -e 2 -f +preposition-determiner-pause -f +determiner+preposition+past -T | grep -iw ka | grep -iw i | tee output/results/ka-i.txt
    python3 -m sentence.query -e 2 -f +preposition-determiner-pause -f +determiner+preposition+goal -T | grep -iw ka | grep -iw ki | tee output/results/ka-ki.txt

    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner-preposition -f +determiner+preposition-past -T | grep -iw ka | grep -iw e | tee output/results/ka-S-e.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner-preposition -f +determiner+preposition+past -T | grep -iw ka | grep -iw i | tee output/results/ka-S-i.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner-preposition -f +determiner+preposition+goal -T | grep -iw ka | grep -iw ki | tee output/results/ka-S-ki.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition-past -f +determiner-preposition -T | grep -iw ka | grep -iw e | tee output/results/ka-e-S.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition+past -f +determiner-preposition -T | grep -iw ka | grep -iw i | tee output/results/ka-i-S.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition+goal -f +determiner-preposition -T | grep -iw ka | grep -iw ki | tee output/results/ka-ki-S.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition+goal -f +determiner+preposition-past -T | grep -iw ka | grep -iw e | grep -iw ki | tee output/results/ka-ki-e.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition+goal -f +determiner+preposition+past -T | grep -iw ka | grep -iw i | grep -iw ki | tee output/results/ka-ki-i.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition-past -f +determiner+preposition+goal -T | grep -iw ka | grep -iw e | grep -iw ki | tee output/results/ka-e-ki.txt
    python3 -m sentence.query -e 3 -f +preposition-determiner-pause -f +determiner+preposition+past -f +determiner+preposition+goal -T | grep -iw ka | grep -iw i | grep -iw ki | tee output/results/ka-i-ki.txt
fi

if [[ $query = "poss" ]]; then
    python3 -m sentence.query -e 1 -f +determiner+possessive+alienable -T | grep -Ei "\b(tā|ā)" | cut -d ' ' -f 3- | tee output/results/poss.A.txt
    python3 -m sentence.query -e 1 -f +determiner+possessive-alienable -T | grep -Ei "\b(tō|ō)" | cut -d ' ' -f 3- | tee output/results/poss.O.txt
fi

if [[ $base = "ka" ]]; then
    for file in output/results/ka*; do
        filename=$(basename $file)
        phrases=$(echo "$filename" | awk -F'-' '{print NF}')
        cat "$file" | cut -d ' ' -f 3- | python3 -m sentence.query -b -i -e $phrases -f +preposition-determiner | sed 's/ /,/g' | tee output/bases/$filename
    done
fi
