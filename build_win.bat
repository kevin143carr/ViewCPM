@echo off
echo ************************ BUILDING WINDOWS COMPATIBLE VIEWCPM  ********************************

set BUILD_DIR=%~dp0staging
set EXE_NAME=viewcpm.exe
set ZIP_NAME=viewcpm_win.zip

mkdir staging

echo ***************************** BUILDING .EXE WITH NUITKA **************************************
python -m nuitka --onefile --standalone --msvc=latest --enable-plugin=tk-inter --output-dir=staging viewcpm.py
cd staging
copy ..\viewcpm_prefs.json.win viewcpm_prefs.json
xcopy ..\support\win\libdskcpmtools .\support\win\libdskcpmtools /E /I /H /Y
echo ***************************** CLEANING UP FOLDERS **************************************
rmdir /s /q viewcpm.build
rmdir /s /q viewcpm.dist
rmdir /s /q viewcpm.onefile-build

REM ===============================
REM CREATE ZIP ARCHIVE
REM ===============================

REM Windows 10/11: use PowerShell Compress-Archive
echo ***************************** COMPRESSING DISTROBUTION **************************************
powershell -Command "Compress-Archive -Path '%BUILD_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

echo ***************************** MOVING DISTROBUTION **************************************
cd ..
mkdir dist

echo ***************************** CLEANING DIST FOLDER **************************************
for /d %%D in ("dist\*") do rmdir /s /q "%%D"
for %%F in ("dist\*") do (
    if /I not "%%~xF"==".zip" del /q "%%F"
)

echo ***************************** COPYING TO DIST FOLDER **************************************
cd dist
xcopy /Y ..\staging\viewcpm_win.zip .
cd ..
rmdir /s /q staging


REM DEBUG ONLY
REM mkdir dist\viewcpm_win
REM tar -xf dist\viewcpm_win.zip -C dist\viewcpm_win