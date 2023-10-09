#!/bin/bash

# for filepath in inputs/SIMPLE-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SIMPLE/
# done

# for filepath in inputs/AMBA-2-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/AMBA-2/
# done

# for filepath in inputs/SYNTECH15-UNREAL-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH15-UNREAL/
# done

# for filepath in inputs/SYNTECH15-1UNREAL-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH15-1UNREAL/
# dones

for filepath in inputs/SYNTECH15-1UNREAL-ORIGINAL/*.spectra
do
        python Spectra2RATSY.py ${filepath} outputs/SYNTECH15-1UNREAL-RAT/
done