#!/bin/sh
a=`pip show ttkthemes | grep Version 1>/dev/null`
if [ "x$a" ] ; then
  . preinstall.csh
fi
