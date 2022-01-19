#!/bin/sh
a=`pip show ttkthemes | grep Version`
if [ "x$a" == "x" ] ; then
  . ./preinstall.csh
fi
