#!/bin/bash

for filepath in inputs/SIMPLE/*.spectra
do
        python translator.py ${filepath} outputs/SIMPLE
done

for filepath in inputs/AMBA-ORIGINAL/*.spectra
do
        python translator.py ${filepath} outputs/AMBA
done

# for filepath in inputs/SYNTECH15-UNREAL-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH15-UNREAL/
# done

# for filepath in inputs/SYNTECH15-1UNREAL-ORIGINAL/*.spectra
# do
#         python translator.py ${filepath} outputs/SYNTECH15-1UNREAL/
# done
