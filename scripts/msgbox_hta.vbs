Function OpenDialog(msg_html, box_w, box_h, msg_title)
	hta_path = "temp_msgform.hta"
	CreateHtaFile hta_path, msg_html, box_w, box_h, msg_title
	Set f = fso.GetFile(hta_path)
	f.attributes = f.attributes + 2 'Hidden
	Dim oShell: Set oShell = CreateObject("WScript.Shell")
	oShell.Run """" & hta_path & """", 1, True
	If fso.FileExists(hta_path) Then
		fso.DeleteFile hta_path
	End If
End Function

Sub CreateHtaFile(hta_path, msg_html, box_w, box_h, msg_title)
	Set f = fso.CreateTextFile(hta_path, True)
	f.WriteLine "<html><title>" & msg_title & "</title>"
	f.WriteLine "<head><HTA:APPLICATION ID=oHTA SINGLEINSTANCE=""yes"" SCROLL=""yes""/></head>"
	f.WriteLine "<script language=""vbscript"">"
	f.WriteLine "Window.ResizeTo " & box_w & ", " & box_h 
	f.WriteLine "</script>"
	f.WriteLine "<body>"
	f.WriteLine msg_html
	f.WriteLine "</body></html>"
	f.Close
End Sub

Set fso = CreateObject("Scripting.FileSystemObject") 

msg_html = "<h2>Message</h2>" & _
	"<p align=center>" & _
	"<input type='button' value='Close' onclick='self.Close()'>" & _
	"</p>"

OpenDialog msg_html, 400, 300, "TITLE HERE"