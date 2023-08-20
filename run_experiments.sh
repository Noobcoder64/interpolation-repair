#!/bin/bash

# for filepath in inputs/AMBA/*.spectra
# do
#         python refinement_fifo_search_duplicatecheck.py ${filepath}
# done

# for filepath in inputs/SYNTECH15-UNREAL/*.spectra
# do
#         python refinement_fifo_search_duplicatecheck.py ${filepath}
# done

for filepath in inputs/SYNTECH15-1UNREAL/*.spectra; do
    filename=$(basename "$filepath")
    output_filename="outputs/${filename%.*}_log.txt"
    
    echo "Repairing $filename"
    
    python refinement_fifo_search_duplicatecheck.py "$filepath" >> "$output_filename" 2>&1
done
