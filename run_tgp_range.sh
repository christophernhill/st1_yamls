#!/bin/bash

# Loop through TGP values from 1.5 to 2.1 in steps of 0.1
for tgp in 1.5 1.6 1.7 1.8 1.9 2.0 2.1
do
    echo "Running with TGP value: $tgp"
    python read_yamls.py --tgp $tgp
    echo "----------------------------------------"
done

# Create combined filename with TGP range information
start_tgp="1p5"
end_tgp="2p1"
step="0p1"
combined_file="summary_ST1-TGP${start_tgp}-${end_tgp}-step${step}.csv"

# Concatenate all CSV files with blank lines between them
for tgp in 1.5 1.6 1.7 1.8 1.9 2.0 2.1
do
    tgp_str=$(echo $tgp | tr '.' 'p')
    cat "summary_ST1-${tgp_str}.csv"
    echo ""  # Add blank line
done > "$combined_file"

echo "All TGP values have been processed."
echo "Combined file created: $combined_file" 