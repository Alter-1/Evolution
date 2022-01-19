@echo off

if exist build.ok del build.ok

pip show pyinstaller | findstr "Version" 1>nul
if errorlevel 1 (  
  pip install pyinstaller
) else (
  goto :ok
)

echo build LifeEmu
pyinstaller.exe -F LifeEmu.py 2> build.log
findstr /C:"SyntaxError:" build.log 1>nul
if %errorlevel% equ 0 (  
  goto :err
)

echo OK > build.ok
echo OK
goto :q

:err

findstr /V INFO build.log
echo !!!
echo !!! Build Error !!!
echo !!!

:q
