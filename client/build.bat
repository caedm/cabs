pyinstaller --onefile --clean --distpath build/pyinstaller/dist ^
    --workpath build/pyinstaller --specpath build/pyinstaller ^
    --name RGSConnect-windows app/src/CABS_client.py
copy build\pyinstaller\dist\cabsagentsvc.exe app\
