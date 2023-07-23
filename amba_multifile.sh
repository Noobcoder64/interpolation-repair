#!/bin/bash
for filepath in Examples/cimattiAnalyzing/*.spectra
do
        python refinement_fifo_search_duplicatecheck.py ${filepath}
done
