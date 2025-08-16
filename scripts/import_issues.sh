#!/bin/bash

# Function to properly parse CSV with embedded commas and quotes
parse_csv_line() {
    local line="$1"
    local -a fields=()
    local field=""
    local in_quotes=false
    local i=0
    
    while [ $i -lt ${#line} ]; do
        char="${line:$i:1}"
        
        if [ "$char" = '"' ]; then
            if [ "$in_quotes" = true ]; then
                # Check if next character is also a quote (escaped quote)
                if [ $((i+1)) -lt ${#line} ] && [ "${line:$((i+1)):1}" = '"' ]; then
                    field+="$char"
                    i=$((i+1))  # Skip the next quote
                else
                    in_quotes=false
                fi
            else
                in_quotes=true
            fi
        elif [ "$char" = ',' ] && [ "$in_quotes" = false ]; then
            fields+=("$field")
            field=""
        else
            field+="$char"
        fi
        
        i=$((i+1))
    done
    
    # Add the last field
    fields+=("$field")
    
    # Return the fields
    for field in "${fields[@]}"; do
        echo "$field"
    done
}

# Read the CSV file, skip header
tail -n +2 issues.csv | while IFS= read -r line; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    # Parse the CSV line
    readarray -t fields < <(parse_csv_line "$line")
    
    # Extract title, body, and labels
    title="${fields[0]}"
    body="${fields[1]}"
    labels="${fields[2]}"
    
    # Clean up any remaining quotes at the beginning and end
    title=$(echo "$title" | sed 's/^"//;s/"$//')
    body=$(echo "$body" | sed 's/^"//;s/"$//')
    labels=$(echo "$labels" | sed 's/^"//;s/"$//')
    
    # Skip if title is empty (malformed row)
    if [ -z "$title" ]; then
        continue
    fi
    
    echo "Creating issue: $title"
    
    # Create the GitHub issue
    gh issue create --title "$title" --body "$body" --label "$labels"
    
    # Optional: Add a small delay to avoid rate limiting
    sleep 1
done