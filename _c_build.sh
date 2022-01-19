#rem // _AT_ 220920 16:52 fresh VS with Python support required

rm ./build.ok

a=`pip show cython | grep Version 1>/dev/null`
if [ "x$a" ] ; then
  pip install cython
  pip install setuptools
fi

a=`pip show ttkthemes | grep Version 1>/dev/null`
if [ "x$a" ] ; then
  call preinstall.csh
fi

python setup.py build_ext --inplace 

python -m compileall LifeEmu.py

cd __pycache__

if [ -s LifeEmu.cpython-37.pyc ] ; then
  if [ -s LifeEmu.pyc  ] ; then
    rm LifeEmu.pyc
  fi
  mv LifeEmu.cpython-37.pyc LifeEmu.pyc
  cp LifeEmu.pyc ../PYD_Files
  echo "done" > "../build.ok"
else
  echo !!!!!
  echo !!!!! BUILD ERROR !!!!
  echo !!!!!
fi

