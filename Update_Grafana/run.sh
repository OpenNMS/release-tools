#!/bin/bash

# Run the python script to download the latest Grafana RPM 
python3 main.py

rpmcount=$(find downloads -name "*.rpm" | wc -l | xargs)

if [ $rpmcount -gt 1 ]
then 
 echo "We have found ${rpmcount} RPM's... we are not sure which one to work with. Exiting!"
 exit
fi

rpmfile=$(find downloads -name "*.rpm")

echo "We want to process ${rpmfile}"

# Place logic to re-sign the rpm files
# rpmsign --resign ${rpmfile}

# move to the final destination
# mv ${rpmfile} /.../.../