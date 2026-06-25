Set shell = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
q = Chr(34)

If CanRun("py -3 --version") Then
  shell.Run "cmd.exe /c py -3 " & q & folder & "\app.pyw" & q, 0, False
ElseIf CanRun("pythonw --version") Then
  shell.Run "cmd.exe /c pythonw " & q & folder & "\app.pyw" & q, 0, False
ElseIf CanRun("python --version") Then
  shell.Run "cmd.exe /c python " & q & folder & "\app.py" & q, 0, False
Else
  MsgBox "Python was not found. Install Python 3, then run:" & vbCrLf & _
         "py -3 -m pip install -r requirements.txt", vbCritical, "GUI Template"
End If

Function CanRun(command)
  CanRun = (shell.Run("cmd.exe /c " & command & " >nul 2>nul", 0, True) = 0)
End Function
