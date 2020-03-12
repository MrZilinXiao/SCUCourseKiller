#!/bin/sh

PROCESS=`ps -ef|grep celery|grep -v grep|grep -v PPID|awk '{ print $2}'`
for i in $PROCESS
do
  echo "Kill the $1 process [ $i ]"
  kill -15 $i
done
