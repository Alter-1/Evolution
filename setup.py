#!/usr/bin/python
# run this file in order to create pyd files

# command to run from cmd. from working directory
# python setup.py build_ext --inplace
#----------------------------------------------

import shutil
import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import sys
# its win32, maybe there is win64 too?
is_windows = sys.platform.startswith('win')
if is_windows:
    from win32api import OutputDebugString
#end if is_windows

setup_list = [ \
    'World', \
    'RtspFrame', \
    'ods', \
    'AsyncTTKQ', \
    'AsyncTextBox', \
    ]

#--- create *.pyx files, generate *.pyd files, delete *.pyx files ---
for fn in setup_list:

    fn_py=fn+".py"
    fn_pyx=fn+".pyx"
    if(is_windows):
        fn_pyd=fn+".cp37-win_amd64.pyd"
    else:
        fn_pyd=fn+".cpython-37m-x86_64-linux-gnu.so"
    #end if is_windows

    pytime = 0
    print("Compile: "+fn_py)

    if not os.path.getmtime(fn_py):
        print("Missing file: "+fn_py)
    else:
        pytime = os.path.getmtime(fn_py)

    pydtime = 0
    if(os.path.exists("PYD_Files")):
        if(os.path.exists("PYD_Files/"+fn_pyd)):
            pydtime = os.path.getmtime("PYD_Files/"+fn_pyd)

    #if(os.path.exists(fn_pyx)):
    #    pyxtime = os.path.getmtime(fn_pyx)

    #print(str(pydtime)+" vs "+str(pytime))
    if(pydtime >= pytime):
        print(fn_py+": No rebuild required, .PYD is newer than .PY")
    else:
        print("Build: "+str(pydtime)+" vs "+str(pytime))
        shutil.copyfile(fn_py, fn_pyx)
        setup(name=fn, ext_modules=cythonize(fn_pyx, compiler_directives={'language_level': "3"}))

#--- delete "build" folder
if os.path.exists("build"):
    shutil.rmtree("build")


#-- create folder with new generated *.pyd files
if not os.path.exists("PYD_Files"):
    os.mkdir('PYD_Files')

#--- run over all the files
for f in os.listdir('.'):  
    if f.endswith(".c") or f.endswith(".pyx"):  # delete all new generated *.c files
        print("remove "+f)
        os.remove(f)
    elif f.endswith(".pyd") or f.endswith(".so"): # move *.pyd files to directory
        print("process "+f)
        if os.path.exists('PYD_Files/'+f):
            print("remove "+'PYD_Files/'+f)
            os.remove('PYD_Files/'+f)
        shutil.move(f, 'PYD_Files/'+f)




