@echo OFF
rem Run global-crypto-behavior data pulls from CoinMarketCap and Crypto News APIs

set CONDAPATH=E:\Anaconda3
set ENVNAME=dev

rem Activate the base environment
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Run the python script for the data pull
python C:\Users\JasonGarcia24\Desktop\global-crypto-behavior\app.py

rem Deactivate the environment
call conda deactivate
