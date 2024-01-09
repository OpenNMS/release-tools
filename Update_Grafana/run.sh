#!/bin/bash

# Run the python script to download the latest Grafana RPM 
python3 main.py

rpmcount=$(find downloads -name "*.rpm" | wc -l | xargs)

if [ $rpmcount -gt 1 ]
then 
 echo "We have found ${rpmcount} RPM's... we are not sure which one to work with. Exiting!"
 exit
fi


if [ $rpmcount -eq 0 ]
then 
 echo "We were unable to find Grafana RPM. Exiting!"
 exit
fi


cd downloads || exit

rpmfile=$(find . -name "*.rpm")

echo "We want to process ${rpmfile}"



if ! sha256sum -c "${rpmfile}.sha256";
then 
echo "Checksum failed! Exiting!"
exit
fi

# Place logic to re-sign the rpm files
# rpmsign --resign ${rpmfile}

# move to the final destination
# mv ${rpmfile} /.../.../