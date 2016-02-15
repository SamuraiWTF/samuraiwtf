#############################################################
Copyright 2010 Sunera, LLC.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Author: Chris Sullo / csullo [at] sunera . com

#############################################################
About

This program attempts to exploit WebDAV enabled servers by:
- attempting to create a new directory (MKCOL)
- attempting to put test files of various programming langauges (PUT)
- optionally attempt to put files with .txt extension, then move to executable (MOVE)
- check if files executed or were uploaded properly
- optionally upload a backdoor/shell file for languages which execute

Additionally, this can be used to put an arbitrary file to remote systems.

#############################################################
Requirements

The following PERL modules are required from cpan.org:
	HTTP::DAV
	Getopt::Long

#############################################################
Options

davtest.pl -url url [options]
 -auth+         Authorization like user:password. Supports Basic and Digest only, no NTLM (yet).
 -cleanup       Delete everything uploaded except backdoor/shell files
 -directory+    Postfix of directory to create. This is always prefixed by 'DavTestDir_' and if not specified
                is set to a random string.
 -debug+        HTTP::DAV debug level 1-3. Levels 2 and 3 log request/responses to /tmp/perldav_debug.txt.
 -move          PUT files as .txt and then try to MOVE them to the executable file extension
 -nocreate      Don't create a directory, work at the -url level.
 -quiet         Only print out summary and serious (usually fatal) errors.
 -random name+  Use this string instead of a random string for filenames.
 -sendbd+       Send backdoor files (from backdoors/ directory). See each script's source for how to use it, if
                it's not immediately obvious.
                        auto - for any succeeded test
                        ext - extension matching file name(s) in backdoors/ dir
 -uploadfile+   Upload this file to to the server. This option requires -uploadloc to specify the remote location.
 -uploadloc+    Upload -uploadfile to this location/name. This option requires -uploadfile.
 -url+          Url of the DAV location.

#############################################################
Test Files

Tests are used to determine if the server can execute a certain type of code. Each test may have a 
corresponding backdoor file, but backdoor files *must* have a corresponding test to determine if 
that file type can execute on the server. It is recommended a simple/basic operation for each language
is used--by default, the supplied tests use mathematical calculations, if possible.

Test files are located in the 'test/' directory. Files must be named according to
the type of program file they will become on the server. For example, a file named 'php.txt'
will be put to the server with a .php extension. 

Each file must have two lines, 'content' and 'execmatch'--the body put to the server and regex to 
match to see if it executed. For example, the php.txt contents are:
	content=<?php print 7.8 * 6.4;?>
	execmatch=49.92

Additionally, the token $$FILENAME$$ will be replaced (with the PUT file's name) in the content before
it sent to the server. Embedded newlines (\n) will be converted to actual newlines (to accommodate PERL).

#############################################################
Backdoor files

Backdoor files are located in the 'backdoors/' directory. They must have the match extension for the type 
they will be uploaded for. For example, a php backdoor must have a '.php' extension.

A backdoor file can contain any code you desire, and multiple backdoor files may be used for a file type. 
If multiple files exist for a type, each will be uploaded when appropriate.

A backdoor type (e.g., php) *must* have a corresponding type in the 'tests/' directory, otherwise it will 
never be tested/uploaded.

#############################################################
Examples

Example: Test file uploads at this location url:
		davtest.pl -url http://localhost/davdir

Example: Test file uploads at this location url and send backdoors for any that succeed:
		davtest.pl -url http://localhost/davdir -sendbd auto

Example: Upload a file using authentication, send the perl_cmd.pl backdoor and call it perl.pl on the server:
		davtest.pl -url http://localhost/davdir -auth user:pass -uploadfile backdoors/perl_cmd.pl -uploadloc perl.pl

#############################################################
TODO:
	- NTLM authentication
	- Backdoors for more languages 
	- Validate jhtml test syntax
