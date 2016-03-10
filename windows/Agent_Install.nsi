# Agent_Install.nsi

#--------------------------------

# The name of the installer
Name "CABS Windows Agent"

# The file to write
OutFile "Install_CABS_Agent.exe"

# The default installation directory
InstallDir "C:\Program Files\CABS\Agent"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKLM "Software\CABS_agent" "Install_Dir"

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
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

#--------------------------------

# The stuff to install
Section "CABS Agent (required)"

  SectionIn RO
  
  # Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  # Put file there
  File "CABS_agent.exe"
  
  #Copy over the other items
  CopyFiles $EXEDIR\CABS_agent.conf $INSTDIR
  FindFirst $0 $1 $EXEDIR\*.pem
	DetailPrint 'Found "$EXEDIR\$1"'
	CopyFiles $EXEDIR\$1 $INSTDIR
  FindClose $0
  
  #Install the Service
  Exec '"$INSTDIR\CABS_agent.exe" --startup=auto install'
  Exec '"$INSTDIR\CABS_agent.exe" start'

  
  # Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\CABS_agent "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_agent" "NoRepair" 1
  WriteUninstaller $INSTDIR\uninstaller.exe
  
SectionEnd

Section "Uninstall"
  # Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CABS_agent"
  DeleteRegKey HKLM SOFTWARE\CABS_agent

  Delete $INSTDIR\uninstaller.exe
 
  Delete $INSTDIR\CABS_agent.exe
  Delete $INSTDIR\CABS_agent.conf
  FindFirst $0 $1 $INSTDIR\*.pem
	Delete $INSTDIR\$1
  FindClose $0

SectionEnd
#--------------------------------
