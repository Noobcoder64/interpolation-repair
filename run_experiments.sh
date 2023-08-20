#!/bin/bash

# for filepath in inputs/AMBA/*.spectra
# do
#         python refinement_fifo_search_duplicatecheck.py ${filepath}
# done

# for filepath in inputs/SYNTECH15-UNREAL/*.spectra
# do
#         python refinement_fifo_search_duplicatecheck.py ${filepath}
# done

for filepath in inputs/SYNTECH15-1UNREAL/*.spectra
do
        python refinement_fifo_search_duplicatecheck.py ${filepath}
done
