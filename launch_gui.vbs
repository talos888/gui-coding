Set shell = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
cmd = "pyw -3 " & Chr(34) & folder & "\app.pyw" & Chr(34)
rc = shell.Run(cmd, 0, True)
If rc <> 0 Then
  cmd = "pythonw " & Chr(34) & folder & "\app.pyw" & Chr(34)
  shell.Run cmd, 0, False
End If
