@echo off
setlocal EnableDelayedExpansion
REM ==========================================================================
REM  build_littlesqrt_vst3.bat
REM  Builds a VST3 plugin (littlesqrt) against the Steinberg VST3 SDK.
REM
REM  Requirements:
REM    - Visual Studio 2022 (or Build Tools) with "Desktop development with C++"
REM    - CMake 3.25+ on PATH
REM    - Git on PATH (only needed if SDK / repo must be cloned)
REM
REM  Usage:
REM    build_littlesqrt_vst3.bat            -> Release build
REM    build_littlesqrt_vst3.bat Debug      -> Debug build
REM    build_littlesqrt_vst3.bat Release install  -> build + copy to VST3 folder
REM                                                  (run as Administrator)
REM ==========================================================================

REM ---------------- CONFIG (edit these) -------------------------------------
set "PLUGIN_NAME=littlesqrt"
set "PLUGIN_REPO=https://github.com/ljrseals-dev/littlesqrt.git"
set "VS_GENERATOR=Visual Studio 17 2022"

REM Folder that holds the plugin source (contains CMakeLists.txt).
REM Default: a "littlesqrt" folder next to this .bat file.
set "PLUGIN_DIR=%~dp0%PLUGIN_NAME%"

REM Folder containing the VST3 SDK (must contain CMakeLists.txt + cmake\).
REM Default: a "vst3sdk" folder next to this .bat file. If it does not exist
REM it is cloned from Steinberg's GitHub.
set "VST3_SDK_ROOT=%~dp0vst3sdk"
REM --------------------------------------------------------------------------

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=Release"
set "DO_INSTALL=%~2"

echo.
echo === Checking tools ===
where cmake >nul 2>&1 || (echo [ERROR] CMake not found on PATH. & goto :fail)

REM ---------------- Get plugin source ---------------------------------------
if not exist "%PLUGIN_DIR%\CMakeLists.txt" (
    echo.
    echo === Plugin source not found, cloning %PLUGIN_REPO% ===
    where git >nul 2>&1 || (echo [ERROR] Git not found on PATH. & goto :fail)
    git clone "%PLUGIN_REPO%" "%PLUGIN_DIR%" || goto :fail
)
if not exist "%PLUGIN_DIR%\CMakeLists.txt" (
    echo [ERROR] No CMakeLists.txt in "%PLUGIN_DIR%".
    echo         The plugin needs a CMakeLists.txt that calls smtg_add_vst3plugin().
    goto :fail
)

REM ---------------- Get VST3 SDK --------------------------------------------
if not exist "%VST3_SDK_ROOT%\CMakeLists.txt" (
    echo.
    echo === VST3 SDK not found, cloning from Steinberg ===
    where git >nul 2>&1 || (echo [ERROR] Git not found on PATH. & goto :fail)
    git clone --recursive https://github.com/steinbergmedia/vst3sdk.git "%VST3_SDK_ROOT%" || goto :fail
)

REM ---------------- Configure -----------------------------------------------
set "BUILD_DIR=%PLUGIN_DIR%\build"
echo.
echo === Configuring (%VS_GENERATOR%, x64) ===
cmake -S "%PLUGIN_DIR%" -B "%BUILD_DIR%" ^
    -G "%VS_GENERATOR%" -A x64 ^
    -DVST3_SDK_ROOT="%VST3_SDK_ROOT%" ^
    -DSMTG_ADD_VST3_PLUGINS_SAMPLES=OFF ^
    -DSMTG_ADD_VSTGUI=OFF ^
    -DSMTG_CREATE_PLUGIN_LINK=OFF ^
    -DSMTG_RUN_VST_VALIDATOR=ON
if errorlevel 1 goto :fail

REM ---------------- Build ---------------------------------------------------
echo.
echo === Building (%CONFIG%) ===
cmake --build "%BUILD_DIR%" --config %CONFIG% --parallel
if errorlevel 1 goto :fail

REM ---------------- Locate output -------------------------------------------
set "VST3_OUT=%BUILD_DIR%\VST3\%CONFIG%\%PLUGIN_NAME%.vst3"
if not exist "%VST3_OUT%" (
    echo.
    echo [WARN] Expected output not found at:
    echo        %VST3_OUT%
    echo        Searching for .vst3 bundles...
    dir /s /b "%BUILD_DIR%\*.vst3" 2>nul
    goto :done
)
echo.
echo Built: %VST3_OUT%

REM ---------------- Install (optional) --------------------------------------
if /i "%DO_INSTALL%"=="install" (
    set "VST3_DEST=%CommonProgramFiles%\VST3"
    echo.
    echo === Installing to !VST3_DEST! ===
    net session >nul 2>&1 || (echo [ERROR] Run this script as Administrator to install. & goto :fail)
    if not exist "!VST3_DEST!" mkdir "!VST3_DEST!"
    xcopy "%VST3_OUT%" "!VST3_DEST!\%PLUGIN_NAME%.vst3\" /E /I /Y >nul || goto :fail
    echo Installed. Rescan plugins in your DAW.
)

:done
echo.
echo === Done ===
endlocal
exit /b 0

:fail
echo.
echo === Build FAILED ===
endlocal
exit /b 1
