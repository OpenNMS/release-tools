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
echo "docs/modules/releasenotes/pages/changelog.adoc"
echo "debian/changelog"
echo "opennms-assemblies/minion/src/main/filtered/debian/changelog"
echo "opennms-assemblies/sentinel/src/main/filtered/debian/changelog"



#find . \
#  -type f \
#  '!' -path './.git/*' \
#  '!' -path '*/node_modules/*' \
#  -print0 \
#  -name \*pom.xml \
#  -o -name features.xml \
#  -o -name \*.adoc \
#  -o -name \*.java \
#  -o -name \*.js \
#  -o -name \*.json \
#  -o -name \*.md \
#  -o -name \*.yml \
#  | xargs -0 perl -pi -e "s,${VERSION}.SNAPSHOT,${VERSION},g" && \
#  if [ -d docs ]; then \
#    perl -pi -e "s,${VERSION%.*.*}-SNAPSHOT,${VERSION%.*.*},g" docs/*.yml; \
#  fi
#echo $?
#
#perl -pi -e 's,"DEBUG","WARN",g' opennms-base-assembly/src/main/filtered/etc/log4j2.xml
#echo $?
#perl -pi -e 's, DEBUG , WARN ,g; s,= DEBUG,= WARN,g' container/karaf/src/main/filtered-resources/etc/org.ops4j.pax.logging.cfg
#echo $?
#
#perl -pi -e 's,("manager" *value=)"WARN",$1"DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml
#echo $?
#perl -pi -e 's,root level="WARN",root level="DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml
#echo $?
#perl -pi -e 's,defaultThreshold="WARN",defaultThreshold="DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml
#echo $?
#
#git commit -a -m "OpenNMS Horizon $VERSION"
#echo $?
#git push
#echo $?

#echo Horizon: https://app.circleci.com/pipelines/github/OpenNMS/opennms?branch=master-${VERSION%.*.*}
