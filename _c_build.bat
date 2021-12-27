rem // _AT_ 220920 16:52 fresh VS with Python support required

del "%PATH_SRC%\build.ok"

pip show cython | findstr "Version" 1>nul
if errorlevel 1 (  
  pip install cython
) else (
  goto :ok
)

:ok
set VS90COMNTOOLS=%VS140COMNTOOLS%

python setup.py build_ext --inplace 

python -m compileall LifeEmu.py

cd __pycache__
if not exist LifeEmu.cpython-37.pyc goto :build_err
goto :build_ok
:build_err
@rem @echo !!!!!
@rem @echo !!!!! BUILD ERROR !!!!
@rem @echo !!!!!
@rem goto :err

:build_ok
if exist LifeEmu.pyc del LifeEmu.pyc
rename LifeEmu.cpython-37.pyc LifeEmu.pyc
copy LifeEmu.pyc ..\PYD_Files
echo "done" > "%PATH_SRC%\build.ok"
:q

:err