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
# done

for filepath in inputs/addedVarsRG1/*.spectra
do
        python translator.py ${filepath} outputs/addedVarsRG1/
done

for filepath in inputs/addedVarsLift/*.spectra
do
        python translator.py ${filepath} outputs/addedVarsLift/
done

for filepath in inputs/addedVarsHumanoid458/*.spectra
do
        python translator.py ${filepath} outputs/addedVarsHumanoid458/
done

for filepath in inputs/addedVarsGyro_Var1/*.spectra
do
        python translator.py ${filepath} outputs/addedVarsGyro_Var1/
done
