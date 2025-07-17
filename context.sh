#!/bin/zsh

if [[ -z "$1" ]]; then
    echo "Usage: $0 <file>"
    exit 1
fi

file="$1"

if [[ ! -f "$file" ]]; then
    echo "Error: File '$file' not found."
    exit 1
fi

# Extract the filename without the path
filename=$(basename "$file")
# Create the context directory if it doesn't exist
mkdir -p "$(dirname "$file")/../context"
output_file="$(dirname "$file")/../context/$filename"

# Redirect output to the new file
exec 3>&1
if [[ "$2" == "-v" ]]; then
    exec > >(tee "$output_file")
else
    exec > "$output_file"
fi

while IFS=' ' read -r document lineNum rest; do
    document=$(echo "$document" | grep -o '[0-9]\+')
    target=$(echo "$rest" | grep -o "\'.*\'" | sed "s/^'//;s/'$//")

    echo $document $lineNum
    python3 -m mbc -d "$document" -g "$lineNum" -b +stop | while IFS=' ' read -r label line; do
        line=$(echo "$line" | grep -o "\'.*\'" | sed "s/^'//;s/'$//")
        if [[ "$line" == *"$target"* ]]; then
            echo "\t$line"
        fi
    done
done < "$file"

{
    echo "Output written to $(realpath "$output_file")"
} 1>&3