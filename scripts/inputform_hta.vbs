Set fso = CreateObject("Scripting.FileSystemObject") 

sHtml = "<div>Value 1 " & _
    "<input id='txt1' style='width: 100px'>" & _
  "</div>" & _
  "<div>Value 2 " & _
    "<select id='txt2' style='width: 100px'>" & _
      "<option value='A'>A</option>" & _
      "<option value='B'>B</option>" & _
      "<option value='C'>D</option>" & _
    "</select>" & _
  "</div>" & _
  "<p align=center>" & _
    "<input type='button' value='Send' onclick='Send()'> " & _
    "<input type='button' value='Close' onclick='self.Close()'>" & _
  "</p>"

  Set oRet = OpenDialog(sHtml, "txt1,txt2", 300, 200, "Dialog 1")
  MsgBox "Value 1: " & oRet("txt1") & ", Value 2: " & oRet("txt2")

'==================================
Function OpenDialog(sHtml, sFields,iWidth,iHeight, sTitle)
  sHtaFilePath = Wscript.ScriptFullName & ".hta"

  CreateHtaFile sHtaFilePath, sHtml, sFields,iWidth,iHeight,sTitle

  Set f = fso.GetFile(sHtaFilePath)
  f.attributes = f.attributes + 2 'Hidden

  Dim oShell: Set oShell = CreateObject("WScript.Shell")

  oShell.Run """" & sHtaFilePath & """", 1, True

  If fso.FileExists(sHtaFilePath) Then
    fso.DeleteFile sHtaFilePath
  End If

  Set oRet = CreateObject("Scripting.Dictionary")

  'Load return data from XML File
  If fso.FileExists(sHtaFilePath & ".xml") Then
      Set oXml = CreateObject("Microsoft.XMLDOM")
      oXML.async = False
      oXML.load sHtaFilePath & ".xml"

      For each sField In Split(sFields,",")
        oRet.Add trim(sField), oXML.SelectSingleNode("/root/" & trim(sField)).text
      Next

      fso.DeleteFile sHtaFilePath & ".xml"
  End If

  Set OpenDialog = oRet
End Function

Sub CreateHtaFile(sHtaFilePath, sHtml, sFields, iWidth, iHeight, sTitle)
  Set f = fso.CreateTextFile(sHtaFilePath, True)
  f.WriteLine "<html><title>FL Reporting</title><head><HTA:APPLICATION ID=oHTA SINGLEINSTANCE=""yes"" SCROLL=""no""/></head>"
  f.WriteLine "<script language=""vbscript"">"
  f.WriteLine "Window.ResizeTo " & iWidth & ", " & iHeight
  f.WriteLine "Set fso = CreateObject(""Scripting.FileSystemObject"")"
  f.WriteLine ""
  f.WriteLine "Sub Send()"
  f.WriteLine " Dim sFilePath: sFilePath = Replace(location.href,""file:///"","""")"
  f.WriteLine " sFilePath = Replace(sFilePath,""/"",""\"")"
  f.WriteLine " sFilePath = Replace(sFilePath,""%20"","" "")"
  f.WriteLine " Set oXml = CreateObject(""Microsoft.XMLDOM"")"
  f.WriteLine " Set oRoot = oXml.createElement(""root"")"
  f.WriteLine " oXml.appendChild oRoot"

  For each sField In Split(sFields,",")
    f.WriteLine " AddXmlVal oXml, oRoot, """ & sField & """, GetVal(" & sField & ")"
  Next

  f.WriteLine " oXml.Save sFilePath & "".xml"""
  f.WriteLine " self.Close()"
  f.WriteLine "End Sub"
  f.WriteLine ""
  f.WriteLine "Sub AddXmlVal(oXml, oRoot, sName, sVal)"
  f.WriteLine " Set oNode = oXml.createElement(sName)"
  f.WriteLine " oNode.Text = sVal"
  f.WriteLine " oRoot.appendChild oNode"
  f.WriteLine "End Sub"
  f.WriteLine ""
  f.WriteLine "Function GetVal(o)"
  f.WriteLine " GetVal = o.value"
  f.WriteLine " If o.Type = ""checkbox"" Then"
  f.WriteLine "   If o.checked = False Then"
  f.WriteLine "     GetVal = """""
  f.WriteLine "   End If"
  f.WriteLine " End If"
  f.WriteLine "End Function"  
  f.WriteLine "</script>"
  f.WriteLine "<body>"
  f.WriteLine sHtml
  f.WriteLine "</body></html>"
  f.Close
End Sub