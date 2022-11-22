#!/bin/bash

export VERSION=31.0.1

export ProductLine=Horizon

if [ $ProductLine == Horizon ]; then
   export REPO_URL=https://github.com/OpenNMS/opennms.git
   export FolderName=horizon
else
   export REPO_URL=https://github.com/OpenNMS/opennms-prime.git 
   export FolderName=meridian
fi

export LOGDIR=$(pwd)/logs

mkdir "$LOGDIR"

mkdir $FolderName

cd $FolderName || exit
mkdir $VERSION
cd $VERSION || exit

echo "Working Directory: $(pwd)" > $LOGDIR/$FolderName.txt 2>&1

git clone $REPO_URL
return_code=$?
echo "Git Clone RC: $return_code" >> $LOGDIR/$FolderName.txt 2>&1
if [ $return_code -ne 0 ]; then
 echo "An error occured during clone step"
 exit $return_code
fi 

cd opennms || exit
git checkout master-${VERSION%.*.*} 
return_code=$?
echo "Git Checkout RC: $return_code" >> $LOGDIR/$FolderName.txt 2>&1
if [ $return_code -ne 0 ]; then
 echo "An error occured during checkout step"
 exit $return_code
fi 

git pull
return_code=$?
echo "Git pull RC: $return_code" >> $LOGDIR/$FolderName.txt 2>&1
if [ $return_code -ne 0 ]; then
 echo "An error occured during pull step"
 exit $return_code
fi 

git merge origin/release-${VERSION%.*.*}.x
return_code=$?
echo "Git Merge RC: $return_code" >> $LOGDIR/$FolderName.txt 2>&1
if [ $return_code -ne 0 ]; then
 echo "An error occured during merge step"
 exit $return_code
fi 
echo ""
echo ""
echo "Verify the changelogs and release note"
echo "Current path: $(pwd)"

if [ $ProductLine == Horizon ]; then
   echo "docs/modules/releasenotes/pages/changelog.adoc"
   echo "debian/changelog"
   echo "opennms-assemblies/minion/src/main/filtered/debian/changelog"
   echo "opennms-assemblies/sentinel/src/main/filtered/debian/changelog"
else
 # Assume we are on the Meridian Product Line
 if [ ${VERSION%.*.*} -ge 2021 ]; then
   echo "docs/modules/releasenotes/pages/changelog.adoc"
 elif  [ ${VERSION%.*.*} -le 2020 ]; then
   echo "opennms-doc/releasenotes/src/asciidoc/releasenotes/whatsnew-${VERSION%.*.*}.adoc"
 fi 
fi