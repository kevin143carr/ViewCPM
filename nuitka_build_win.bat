@echo off
echo ************************ BUILDING WINDOWS COMPATIBLE VIEWCPM  ********************************

set BUILD_DIR=%~dp0staging
set EXE_NAME=viewcpm.exe
set ZIP_NAME=viewcpm_win.zip

mkdir staging

echo ***************************** BUILDING .EXE WITH NUITKA **************************************
python -m nuitka --onefile --standalone --msvc=latest --enable-plugin=tk-inter --windows-disable-console --output-dir=staging viewcpm.py
cd staging
copy ..\viewcpm_prefs.json.win viewcpm_prefs.json
xcopy ..\support\win\libdskcpmtools .\support\win\libdskcpmtools /E /I /H /Y
echo ***************************** CLEANING UP FOLDERS **************************************
rmdir /s /q viewcpm.build
rmdir /s /q viewcpm.dist
rmdir /s /q viewcpm.onefile-build

REM ===============================
REM 3️⃣ CREATE ZIP ARCHIVE
REM ===============================

REM Windows 10/11: use PowerShell Compress-Archive
echo ***************************** COMPRESSING DISTROBUTION **************************************
powershell -Command "Compress-Archive -Path '%BUILD_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

echo ***************************** MOVING DISTROBUTION **************************************
cd ..
mkdir dist
cd dist
xcopy /Y ..\staging\viewcpm_win.zip .
cd ..
rmdir /s /q staging