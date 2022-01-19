pip show ttkthemes | findstr "Version" 1>nul
if errorlevel 1 (  
  call preinstall.cmd
)
