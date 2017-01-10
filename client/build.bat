pyinstaller --onefile --clean --noconsole --distpath build/pyinstaller/dist ^
    --workpath build/pyinstaller --specpath build/pyinstaller ^
    --name RGSConnect-windows app/src/CABS_client.py
@echo off
echo build complete.
pause
