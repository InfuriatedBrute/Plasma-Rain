:: cd to directory of batch file
::cd ~dp%0



:: Option 1: Output to console in realtime
py src\engine.py

:: Option 2: Redirect output to log.txt then print log.txt to console after program exit
:: py src\engine.py 1> data\logs\log.txt 2>&1
:: type data\logs\log.txt
