# Client_Install.nsi

#--------------------------------

# The name of the installer
Name "CABS Windows Client"

# The file to write
OutFile "Install_CABS_Client.exe"

# The default installation directory
InstallDir "C:\Program Files\CABS\Client"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKLM "Software\CABS_client" "Install_Dir"

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
Page license
Page components
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

#--------------------------------

# The stuff to install
Section "CABS Client (required)"

  SectionIn RO
  
  # Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  # Put file there
  File "CABS_client.exe"
  File "Header.png"
  File "Icon.ico"
  
  #Copy over the other items
  CopyFiles $EXEDIR\CABS_client.conf $INSTDIR
  FindFirst $0 $1 $EXEDIR\*.pem
	DetailPrint 'Found "$EXEDIR\$1"'
	CopyFiles $EXEDIR\$1 $INSTDIR
  FindClose $0
  
  # Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\CABS_client "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_client" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_client" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_client" "NoRepair" 1
  WriteUninstaller $INSTDIR\uninstaller.exe
  
SectionEnd

# Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\CABS"
  CreateShortcut "$SMPROGRAMS\CABS\Uninstaller.lnk" "$INSTDIR\uninstaller.exe" "" "$INSTDIR\uninstaller.exe" 0
  CreateShortcut "$SMPROGRAMS\CABS\CABS_Client.lnk" "$INSTDIR\CABS_client.exe" "" "$INSTDIR\Icon.ico" 0
  
SectionEnd

Section "Uninstall"
  # Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_client"
  DeleteRegKey HKLM SOFTWARE\CABS_client

  Delete $INSTDIR\uninstaller.exe
 
  Delete $INSTDIR\CABS_client.exe
  Delete $INSTDIR\Header.png
  Delete $INSTDIR\Icon.ico
  Delete $INSTDIR\CABS_client.conf
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
