Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run chr(34) & currentDir & "\venv\Scripts\pythonw.exe" & Chr(34) & " " & Chr(34) & currentDir & "\nightlock.py" & Chr(34), 0
Set WshShell = Nothing
