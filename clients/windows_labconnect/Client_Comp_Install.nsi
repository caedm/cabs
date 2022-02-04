# Client_Install.nsi
!include "MUI2.nsh"
!include x64.nsh


Function setpath
Var  /Global uninstpath

	${If} ${RunningX64}
		StrCpy $uninstpath "SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\"
	${Else}
		StrCpy $uninstpath "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\"
	${EndIf}   
FunctionEnd


#--------------------------------

# The name of the installer
Name "Lab Connect Windows Client"

# The file to write
OutFile "Install_Lab_Connect.exe"

# The default installation directory
InstallDir "C:\Program Files\Lab_Connect\Client"

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically)
InstallDirRegKey HKLM "Software\Lab_Connect" "Install_Dir"

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
#Page components
#Page directory
#Page instfiles
#UninstPage uninstConfirm
#UninstPage instfiles

!define MUI_ABORTWARNING

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
  
  !insertmacro MUI_LANGUAGE "English"

#--------------------------------
# The stuff to install

Section "Lab Connect (required)" SecLabConnect

  SectionIn RO
  
  #check to see if they have an old version
	#as new versions are released, add the product code here so they can be checked for because the installer won't remove them automatically and it will silently fail
		
	#Check for current installation for LabConnect
	IfFileExists $INSTDIR\*.* file_found file_not_found

	file_not_found:
		#LabConnect not installed
		Goto done
	file_found:
		#LabConnect is installed - we need to remove it first, but it will probably require a reboot
		MessageBox MB_OK "An old version of LabConnect client is already installed. We will remove it now."
		  DeleteRegKey HKLM SOFTWARE\Lab_Connect
		  Delete "$INSTDIR\LabConnect.exe"
		  Delete $INSTDIR\Header.png
		  Delete $INSTDIR\Icon.ico
		  Delete $INSTDIR\LabConnect.conf
		  Delete $INSTDIR\caedm_noprompt.rdp
		  Delete $INSTDIR\Connect-Mstsc.ps1
			FindFirst $0 $1 $INSTDIR\*.pem
				Delete $INSTDIR\$1
			FindClose $0
		  # Remove shortcuts
		  Delete "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\LabConnect.exe"

		  # Remove directories used
		  RMDir "$INSTDIR"
		#Abort "You must reboot to continue installation. Click Cancel, then Reboot your computer and run this installer again."
		Goto done
	done:
	
  # Set output path to the installation directory.
  SetOutPath $INSTDIR
 
  # Put file there
  File "LabConnect.exe"
  File "Header.png"
  File "Icon.ico"
  
  #Copy over the other items
  File "LabConnect.conf"
  File "cert.pem"
  
  # Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\Lab_Connect "Install_Dir" "$INSTDIR"
  #WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "UninstallString" '"$INSTDIR\uninstall.exe"'
  #WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "NoModify" 1
  #WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\RGSConnect" "NoRepair" 1
  #WriteUninstaller $INSTDIR\uninstaller.exe
  
SectionEnd


# Optional section (can be disabled by the user)
Section "Start Menu Shortcuts" SecShortcuts

  #CreateDirectory "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\RGSConnect"
  #CreateShortcut "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\RGSConnect\Uninstaller.lnk" "$INSTDIR\uninstaller.exe" "" "$INSTDIR\uninstaller.exe" 0
  CreateShortcut "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\LabConnect.lnk" "$INSTDIR\LabConnect.exe" "" "$INSTDIR\Icon.ico" 0
  
SectionEnd

#Section "Uninstall"
  # Remove registry keys
#  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LabConnect"
#  DeleteRegKey HKLM SOFTWARE\Lab_Connect

#  Delete $INSTDIR\uninstaller.exe
 
#  Delete "$INSTDIR\LabConnect.exe"
#  Delete $INSTDIR\Header.png
#  Delete $INSTDIR\Icon.ico
#  Delete $INSTDIR\rgsconnect.conf
#  Delete $INSTDIR\Connect-Mstsc.ps1
#  Delete $INSTDIR\caedm_noprompt.rdp
#  FindFirst $0 $1 $INSTDIR\*.pem
#	Delete $INSTDIR\$1
#  FindClose $0

  # Remove shortcuts
#  Delete "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\LabConnect.exe"

  # Remove directories used
#  RMDir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\RGSConnect"
#  RMDir "$INSTDIR"
  
  #Remove HP RGS Client
#  ExecWait 'MsiExec.exe /x {5754A452-34C8-427A-AC6C-C55EF6200D17} /norestart /qb'
  
#SectionEnd
#--------------------------------

  LangString DESC_SecLabConnect ${LANG_ENGLISH} "Installs the CAEDM Lab Connect Client, which allows you to connect to blade workstation."
  LangString DESC_SecShortcuts ${LANG_ENGLISH} "Creates shortcuts in your start menu to Lab Connect."
  
  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${SecLabConnect} $(DESC_SecLabConnect)
	!insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} $(DESC_SecShortcuts)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END
  
  

