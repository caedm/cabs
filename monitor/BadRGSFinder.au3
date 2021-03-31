; ***************************************************************************************************************************************
;
;	BAD RGS BLADE FINDER SCRIPT
;	Written by Dean and Travis
;  (edited by Sam Beckett 2016)
;
; ***************************************************************************************************************************************

;$InitialList : Computers we got from the broker
;$ListOfBad : Computers who failed our RGS test
;$ListOfBad2 : Computers who failed the second RGS test
;ListOfBad3 : Computers who failed the third RGS test
;ListOfBad4 : Computers who failed the fourth RGS test


StartReceiver()										;Start up the receiver

TestPrev()											;Test the computers who were previously disabled by this script
TestPrev()											;Test the computers previously disabled again (just in case)

Dim $InitialList = GetHostnames()					;Read in the list of computers to check
Local $linecount = UBound($InitialList)

$bad = 0											;Count the number of bad machines
Dim $ListOfBad[999]									;Check each machine and list out the bad ones in $ListOfBad

$i = 0
While $i < $linecount
	$result = TestRGS($InitialList[$i])
	if not($result == "GOOD")  then
		$ListOfBad[$bad] = $InitialList[$i]
		$bad += 1
	 EndIf
	 $i +=1
WEnd

Sleep(30000)
												    ;Recheck the List (for verification purposes)

Dim $ListOfBad2[999]								;This stores a list of computers who fail test 1 & 2
$bad2 = 0

$i = 0
While $i < $bad
	if not($ListOfBad[$i] == "") then
		$result = TestRGS($ListOfBad[$i])
		if not($result == "GOOD")  then				;Store the bad computer names
			$ListOfBad2[$bad2] = $ListOfBad[$i]
			$bad2 += 1
		EndIf
	 endif
	 $i += 1
  WEnd

  if $bad2 / $linecount > .3 Then					;If over 30% of blades are bad...
	  $a = FileOpen("above30.txt", 2)				;Open "above30.txt"
	  for $i = 0 to $bad2							;Write the hostnames in $bad2 to "above30.txt"
	  If not ($ListOfBad2[$i] == "") Then
		 FileWriteLine($a, $ListOfBad2[$i])
	  EndIf
   Next
   FileFlush($a)									;Flush "above30.txt"
   FileClose($a)									;Close "above30.txt"
	run("above30.cmd")								;Send the email
	Exit											;Close the program without making changes
   EndIf


if $bad2 >0 Then									;Loop through $ListOfBad2 and disable/restart sender on each hostname
   for $i = 0 to $bad2
	  RunWait(@ComSpec & ' /c ' & 'send_broker_cmd.py autoit disable ' & $ListOfBad2[$i])
	  RunWait(@ComSpec & ' /c ' & 'send_broker_cmd.py tell_agent restart ' & $ListOfBad2[$i])
   Next
EndIf

Sleep(300000)										;Wait for broker to make changes and computers to restart service

Dim $ListOfBad3[999]								;Holds the computers who failed the 3rd test
$bad3 = 0

$i = 0
While $i < $bad2			   						;Loop through $ListOfBad2 and test them again to see if the fix worked
	if not ($ListOfBad2[$i] = "") Then
	  $result = TestRGS($ListOfBad2[$i])
	If not($result == "GOOD")  then					;If the test did not work, then add them to the $ListOfBad3 array
		$ListOfBad3[$bad3] = $ListOfBad2[$i]
		$bad3 += 1
    Else											;If the test did work, then tell the broker to enable the machine
	RunWait(@ComSpec & ' /c ' & 'send_broker_cmd.py autoit enable ' & $ListOfBad2[$i])
   EndIf
 EndIf

 $i += 1
WEnd


if $bad3 >0 Then									 ;If the restart service command didn't fix the machine, tell the agent to reboot the machine
   for $i = 0 to $bad3
	  RunWait(@ComSpec & ' /c' & 'send_broker_cmd.py tell_agent reboot ' & $ListOfBad3[$i])
   Next
EndIf

Sleep(300000)										;Wait for the broker to issue the command and the machine to restart

Dim $ListOfBad4[999]								;Holds the computers who failed the 4th test
$bad4 = 0

$i = 0
While $i < $bad3									;Loop through $ListOfBad3 (the restarted machines) and test them again
   $result = TestRGS($ListOfBad3[$i])

   If not ($result == "GOOD") Then					;If they're still broken, add them to the $ListOfBad4 array
	  $ListOfBad4[$bad4] = $ListOfBad3[$i]
	  $bad4 += 1
   Else												;If that fixed the problem, enable the machine
	  RunWait(@ComSpec & ' /c' & 'send_broker_cmd.py autoit enable ' & $ListOfBad3[$i])
   EndIf
   $i += 1
WEnd

$fhandle = FileOpen("badblades.txt", 2)				;Write the list of final broken RGS blades to file

if $bad4 > 0 Then
   for $i = 0 to $bad4
	  If not ($ListOfBad4[$i] == "") Then
		 FileWriteLine($fhandle, $ListOfBad4[$i])
	  EndIf
   Next
EndIf


;Send Email
;if $bad4 > 0 then
;	run("reportemail.cmd")
;EndIf

FileFlush($fhandle)									;Close up the file handle, flush to disk
FileClose($fhandle)

KillReceiver()										;Kills RGS Receiver (closes up shop)

exit

; ***************************************************************************************************************************************
;
;	END OF NORMAL PART OF SCRIPT
;	BELOW THIS POINT ARE THE USER DEFINED FUNCTIONS
;
; ***************************************************************************************************************************************

Func GetHostnames()			;This function gets a list of hostnames to check from the broker

   ShellExecute("C:\RGS Tester\broker_query.bat")	;Run broker query command

   Local $ifhandle = FileOpen("output.txt", 0)			;Open "output.txt" which is the broker output
   Local $query[999]									;Array to hold output.txt lines
   Local $linecount = 0									;Linecount object

   SetError(0)

    While 1												;Loop through file, add each line to "query" array, count lines
	  $line = FileReadLine($ifhandle)
	  if @error = -1 Then ExitLoop					;reached end of file
	  If $line <> "" Then
		 $query[$linecount] = $line
		 $linecount += 1
	  EndIf
   WEnd

   Dim $compnames[$linecount]							;Array to hold computer names
   $newsize = 0									    	;Size for new array

   Local $tempo
   Local $tempo2
   Local $tempo3

   $n = 0
   while $n < $linecount								;Loop through lines of file

	  If $n <> 0 Then									;Skip first line
		 If $query[$n] <> "END" Then					;Look at each line that isn't "END"
			Local $templ = StringSplit($query[$n], ",")	;Split each line by comma and add each split to array $templ
			$z = 0
			$tempo2 = $templ[2]
			$tempo = $templ[5]
			If $tempo <> "1" Then						;If the machine is enabled (#5 isn't 1), then...
			   $compnames[$newsize] = $tempo2			;Add the second word (host name) into $compnames array
			   $newsize += 1							;Count how many computer names we're dealing with
			EndIf
		 EndIf
	  EndIf
   $n += 1
WEnd

   ReDim $compnames[$newsize]						;Resize array
   FileClose($ifhandle)								;Close file
   FileFlush($ifhandle)								;Flush file

   Return $compnames

EndFunc

Func TestPrev()				;This function tests previously disabled blades. If they now work, they are enabled again.

   ShellExecute("C:\RGS Tester\broker_query.bat")	;Run broker query command

   Local $bfhandle = FileOpen("output.txt", 0)		;Open "output.txt" which is the broker output
   Local $query[999]								;Array to hold output.txt lines
   Local $linecount = 0								;Linecount object

   SetError(0)										;probably not needed

   While 1												;Loop through file, add each line to "query" array, count lines
	  $line = FileReadLine($bfhandle)
	  if @error = -1 Then ExitLoop					;reached end of file
	  If $line <> "" Then
		 $query[$linecount] = $line
		 $linecount += 1
	  EndIf
   WEnd

   Dim $prevnames[$linecount]						;Array to hold computer names
   $newsize = 0									    ;Size for new array

   Local $tempo
   Local $tempo2

   $n = 0
   $j = 0

   while $n < $linecount								;Loop through lines of file

	  If $n <> 0 Then									;Skip first line
		 If $query[$n] <> "END" Then					;Look at each line that isn't "END"
			Local $templ = StringSplit($query[$n], ",")	;Split each line by comma and add each split to array $templ
			$tempo2 = $templ[2]
			$tempo = $templ[5]
			If $tempo = "1" And $templ[6] = "autoit" Then	;If the machine was previously disabled by this script
			   $prevnames[$newsize] = $tempo2				;Add names to the "prevnames" array
			   $newsize += 1
			EndIf
		 EndIf
	  EndIf

   $n += 1
   WEnd

   FileClose($bfhandle)								;Close file
   FileFlush($bfhandle)								;Flush file


   If $newsize <> 0 Then

	  ReDim $prevnames[$newsize]						;Resize array

	  $i = 0
	  While $i < $newsize								;Loop through names of previously disabled computers
		 $result = TestRGS($prevnames[$i])				;and test them.
		 if($result == "GOOD")  then					;If they check out, then enable them again. Otherwise do nothing.
			RunWait(@ComSpec & ' /c ' & 'send_broker_cmd.py autoit enable ' & $prevnames[$i])
		 EndIf
		 $i +=1
	  WEnd
   EndIf

EndFunc

Func StartReceiver()		;This function starts the receiver and changes its name (must type into Run box)

	Send("{LWINDOWN}r{LWINUP}")
	sleep(500)
	Send("""C:\Program Files (x86)\Hewlett-Packard\Remote Graphics Receiver\rgreceiver.exe""")
	Send("{ENTER}")

	sleep(5000)
	;The title must be unique so that we can separate windows with the same name (might be broken)
	WinSetTitle("HP Remote Graphics Receiver","","All Your RGS Are Belong To Us")

EndFunc

Func TestRGS($hostname)		;This function begins the testing process for a hostname

	dim $result

	SendBackspaces()					;Clear what is in the hostname box

	Send($hostname & "{ENTER}")			;Send the hostname as keys

	$DoesItWork = ItsWorking($hostname)	;Check to see if we saw the authentication dialog

	if $DoesItWork = 1 Then				;If we saw the authentication dialog, return "Good"
		SendTab()
		return "GOOD"
	 endif

	 if $DoesItWork = 2 Then			;If it connected to server to ask for further authentication (usually for Linux), return "Good"
		KillReceiver()					;You have to restart the reciever after this one
		StartReceiver()
		return "GOOD"
	endif

	if $DoesItWork = -1 Then			;If the "it's broken" dialog came up, return "FASTERROR"
		Send("{ENTER}")
		return "FASTERROR"
	endif

	dim $tries							;If the system isn't working, keep trying!

	sleep(1500)

	while $tries <= 5					;Try five more times.
		$DoesItWork = ItsWorking($hostname)

		if $DoesItWork = 1 then			;Finally saw the authentication dialog, return "GOOD"
			SendEscapes()
			return "GOOD"
		 EndIf

		 if $DoesItWork = 2 Then		;Connected to server (linux), return "GOOD"
			KillReceiver()
			StartReceiver()
			return "GOOD"
		 EndIf

		if $DoesItWork = -1 Then		;Still not working, return "SLOWERROR"
			send("{ENTER}")
			return "SLOWERROR"
		endif

		sleep(1500)
		$tries +=1
	WEnd

	;If we get to this point, at least 15 seconds have elapsed and we are giving up
	;The receiver has stuck waiting for a response, but we give up. Restart the reciever so we can keep going.

	KillReceiver()
	StartReceiver()

	Return "TIMEOUT"

EndFunc

Func KillReceiver()			;This function lists all the reciever processes and terminates them.
	$list = ProcessList("rgreceiver.exe")
	for $i = 1 to $list[0][0]
	  ProcessClose($list[$i][1])
	next
EndFunc

Func SendTab()				;This function closes the authentication window by tab tab enter.
   ;Close authentication window by tab tab enter
   send("{TAB}{TAB}{ENTER}")
   sleep(500)
EndFunc

Func SendEscapes()			;This function sends out escapes to clear any dialogs
	;send a bunch of escapes to clear out any dialogs
	send("{ESC}{ESC}{ESC}{ESC}")
	sleep(200)
	send("{ESC}{ESC}{ESC}{ESC}")
	sleep(200)
	send("{ESC}{ESC}{ESC}{ESC}")
	sleep(200)
	send("{ESC}{ESC}{ESC}{ESC}")
endfunc

Func ItsWorking($hostname)	;This function checks to see if the blade is working by looking at the title of message boxes

	;If we see the authentication dialog, it means that the blade is working

	;If we see the HP Remote Graphics dialog, it means that there was a problem

	;It is important to note that by default the receiver has the same title as the dialogs. We have changed the title
	;of the main receiver window to something else in the StartReceiver function because of this.



	Sleep(1500)							;This gives the dialog box time to appear
	$windowcount = 0					;Count of the windows

	$var = WinList("[CLASS:QWidget]")	;HP Reciever windows only appear when you search for QWidget windows

	For $i = 1 to $var[0][0]
	  If $var[$i][0] <> "" AND IsVisible($var[$i][1]) Then		;Only look at visble windows that have a title

		if StringInStr($var[$i][0],"Authenticate to") > 0 then	;This is the window we are looking for
			return 1
		 EndIf

		 if StringInStr($var[$i][0],$hostname) > 0 then			;Immediately connected to $hostame for authentication (Linux)
			return 2
		 EndIf

		if StringInStr($var[$i][0],"HP Remote Graphics Software") > 0 then	;Problem window
			$windowcount += 1
		 EndIf

		 ;The default rgreciever window is called "HP Remote Graphics Software" so we are actually
		 ;looking for the second instance with that name.
		 If $windowcount = 2 Then
		 return -1
		 EndIf

	  EndIf
	Next

	return false	;No windows seen, return false.
EndFunc

Func IsVisible($handle)		;This function determines if a window is visible
  If BitAnd( WinGetState($handle), 2 ) Then
    Return 1
  Else
    Return 0
  EndIf

EndFunc

Func SendBackspaces()		;This function sends a ton of backspaces
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")
   send("{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}{BACKSPACE}")

   EndFunc

