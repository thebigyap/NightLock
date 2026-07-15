Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell")

' Register self as a startup item (HKCU Run key, shows in Task Manager > Startup apps)
runKey = "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\NightLock"
startupCmd = "wscript.exe " & Chr(34) & WScript.ScriptFullName & Chr(34)
On Error Resume Next
existing = WshShell.RegRead(runKey)
isNew = (Err.Number <> 0)
Err.Clear
On Error Goto 0
If existing <> startupCmd Then WshShell.RegWrite runKey, startupCmd, "REG_SZ"
If isNew Then
    WshShell.Popup "NightLock will now start automatically with Windows." & vbCrLf & vbCrLf & _
        "To turn this off: Task Manager > Startup apps > disable NightLock.", 10, "NightLock", 64
End If

WshShell.Run chr(34) & currentDir & "\venv\Scripts\pythonw.exe" & Chr(34) & " " & Chr(34) & currentDir & "\nightlock.py" & Chr(34), 0
Set WshShell = Nothing
