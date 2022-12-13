#!/bin/bash

export VERSION=31.0.2
#export VERSION=2022.1.10

export ProductLine=Horizon
#export ProductLine=Meridian

if [ $ProductLine == Horizon ]; then
   export FolderName=horizon
else
   export FolderName=meridian
fi


export LOGDIR=$(pwd)/logs

cd $FolderName || exit
cd $VERSION || exit
cd opennms*

echo "" >> $LOGDIR/$FolderName.txt 2>&1
echo "=== Part 2 -- 02-set-version.sh ===" >> $LOGDIR/$FolderName.txt 2>&1
echo "Working Directory: $(pwd)" >> $LOGDIR/$FolderName.txt 2>&1

find . \
  -type f \
  '!' -path './.git/*' \
  '!' -path '*/node_modules/*' \
  -print0 \
  -name \*pom.xml \
  -o -name features.xml \
  -o -name \*.adoc \
  -o -name \*.java \
  -o -name \*.js \
  -o -name \*.json \
  -o -name \*.md \
  -o -name \*.yml \
  | xargs -0 perl -pi -e "s,${VERSION}.SNAPSHOT,${VERSION},g" && \
  if [ -d docs ]; then \
    perl -pi -e "s,${VERSION%.*.*}-SNAPSHOT,${VERSION%.*.*},g" docs/*.yml; \
  fi

perl -pi -e 's,"DEBUG","WARN",g' opennms-base-assembly/src/main/filtered/etc/log4j2.xml

perl -pi -e 's, DEBUG , WARN ,g; s,= DEBUG,= WARN,g' container/karaf/src/main/filtered-resources/etc/org.ops4j.pax.logging.cfg

perl -pi -e 's,("manager" *value=)"WARN",$1"DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml

perl -pi -e 's,root level="WARN",root level="DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml

perl -pi -e 's,defaultThreshold="WARN",defaultThreshold="DEBUG",' opennms-base-assembly/src/main/filtered/etc/log4j2.xml

if [ $ProductLine == Horizon ]; then
   git commit -a -m "OpenNMS Horizon $VERSION"
else
   git commit -a -m "OpenNMS Meridian $VERSION"
fi

echo ""
echo "Double check the changes and then run git push"
echo "After running git push, you should be able to see your build at:"
if [ $ProductLine == Horizon ]; then
   echo Horizon: https://app.circleci.com/pipelines/github/OpenNMS/opennms?branch=master-${VERSION%.*.*}
else
   echo Meridian: https://app.circleci.com/pipelines/github/OpenNMS/opennms-prime?branch=master-${VERSION%.*.*}
fi


