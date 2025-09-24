Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run chr(34) & "PATH_TO\run_tracker.bat" & Chr(34), 0
Set WshShell = Nothing
