# Client_Install.nsi

#--------------------------------

# The name of the installer
#Name "CABS Windows Client"
Name "RGSConnect"

# The file to write
#OutFile "Install_CABS_Full_Client.exe"
OutFile "install_rgsconnect-${VERSION}.exe"

# The default installation directory
InstallDir "C:\Program Files\CABS\Client"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKLM "Software\RGSConnect" "Install_Dir"

# Request application privileges for Windows Vista
RequestExecutionLevel admin

#create macro to copy files to non-existant locations
!define FileCopy `!insertmacro FileCopy`
!macro FileCopy FilePath TargetDir
  CreateDirectory `${TargetDir}`
  CopyFiles `${FilePath}` `${TargetDir}`
!macroend
#--------------------------------

# Pages
Page components
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "HP rgreceiver (required)"
    SectionIn RO
    SetOutPath $INSTDIR
    File "ReceiverSetup.exe"
    Exec "$INSTDIR\ReceiverSetup.exe"
SectionEnd

# The stuff to install
Section "RGSConnect (required)"
  SectionIn RO
  
  # Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  # Put file there
  File "RGSConnect.exe"
  File "Header.png"
  File "Icon.png"
  File "icon.ico"
  File "version.txt"
  File "CABS_client.conf"
  File "cert.pem"
  
  # Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\RGSConnect "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "NoRepair" 1
  WriteUninstaller $INSTDIR\uninstaller.exe
  
SectionEnd

# Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\CABS"
  CreateShortcut "$SMPROGRAMS\CABS\Uninstaller.lnk" "$INSTDIR\uninstaller.exe" "" "$INSTDIR\uninstaller.exe" 0
  CreateShortcut "$SMPROGRAMS\CABS\RGSConnect.lnk" "$INSTDIR\RGSConnect.exe" "" "$INSTDIR\icon.ico" 0
  
SectionEnd

Section "Uninstall"
  # Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect"
  DeleteRegKey HKLM SOFTWARE\RGSConnect

  Delete $INSTDIR\uninstaller.exe
 
  Delete $INSTDIR\RGSConnect.exe
  Delete $INSTDIR\Header.png
  Delete $INSTDIR\Icon.png
  Delete $INSTDIR\icon.ico
  Delete $INSTDIR\version.txt
  Delete $INSTDIR\CABS_client.conf
  Delete $INSTDIR\ReceiverSetup.exe
  FindFirst $0 $1 $INSTDIR\*.pem
	Delete $INSTDIR\$1
  FindClose $0

  # Remove shortcuts
  Delete "$SMPROGRAMS\CABS\*.*"

  # Remove directories used
  RMDir "$SMPROGRAMS\CABS"
  RMDir "$INSTDIR"
SectionEnd
#--------------------------------
