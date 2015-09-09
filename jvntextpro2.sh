#!/usr/bin/sh

echo "jvntextpro tool chain"

JVNTEXTPRO_HOME=~/softwares/jvntextpro2

java -mx1024M -cp "${JVNTEXTPRO_HOME}/bin:${JVNTEXTPRO_HOME}/libs/lbfgs.jar:${JVNTEXTPRO_HOME}/libs/args4j.jar" jvnsegmenter.WordSegmenting -modeldir ${JVNTEXTPRO_HOME}/models/jvnsegmenter -inputfile $1

java -mx1024M -cp "${JVNTEXTPRO_HOME}/bin:${JVNTEXTPRO_HOME}/libs/lbfgs.jar:${JVNTEXTPRO_HOME}/libs/args4j.jar" jvnpostag.POSTagging -tagger maxent -modeldir ${JVNTEXTPRO_HOME}/models/jvnpostag/maxent -inputfile $1.wseg

