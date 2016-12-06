pyinstaller --onefile --clean --distpath build\pyinstaller\dist ^
    --workpath build\pyinstaller --specpath build\pyinstaller ^
    app\cabsagentsvc.py
pyinstaller --onefile --clean --distpath build\pyinstaller\dist ^
    --workpath build\pyinstaller --specpath build\pyinstaller ^
    app\checks\pscheck.py
copy build\pyinstaller\dist\cabsagentsvc.exe app\
copy build\pyinstaller\dist\pscheck.exe app\checks\
@echo off
echo build complete.
pause
