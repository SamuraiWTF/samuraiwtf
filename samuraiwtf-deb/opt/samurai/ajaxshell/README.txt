			_________ _______  _        _______ 
			\__   __/(  ___  )| \    /\(  ____ \
			   ) (   | (   ) ||  \  / /| (    \/
			   | |   | (___) ||  (_/ / | (__    
			   | |   |  ___  ||   _ (  |  __)   
			   | |   | (   ) ||  ( \ \ | (      
			   | |   | )   ( ||  /  \ \| (____/\
			   )_(   |/     \||_/    \/(_______/
			                                    
 _______  _______  _       _________ _______  _______  _       
(  ____ \(  ___  )( (    /|\__   __/(  ____ )(  ___  )( \      
| (    \/| (   ) ||  \  ( |   ) (   | (    )|| (   ) || (      
| |      | |   | ||   \ | |   | |   | (____)|| |   | || |      
| |      | |   | || (\ \) |   | |   |     __)| |   | || |      
| |      | |   | || | \   |   | |   | (\ (   | |   | || |      
| (____/\| (___) || )  \  |   | |   | ) \ \__| (___) || (____/\
(_______/(_______)|/    )_)   )_(   |/   \__/(_______)(_______/
                                                               


The shell started as a simple command line thing with AJAX 
and PHP and turned out as a fully functional shell with 
possibilities for plugins, uploading, GUI filebrowsing/editing,
... too much to name. 

The shell's size is pretty neat, 17506 bytes, rough 17kb. This
makes it easy to upload on any host and delete it afterwards
for security reasons(even though it has a password, passwords
can be bruteforced).

The layout can be divided in three parts:
	Tabs
		* File manager
		* File upload
		* File editor
		* Set working directory
		* Command Input
	
	Sidebar
		* Quick Commands (aka Custom Commands)
		* History
		* About
		
	Main output window
		* This contains ALL output but the command history.
		
The shell doesn't really need a big readme, you'll learn to work
with every function in it in a few minutes. I get feedback like
people say they were suprised they could click history items and
repeat the command, for example. Almost everything you see can
be clicked and has a specific/use(ful|less) function :) ! For the
fans, don't think I'm creating this thing for a large public, this
should be one of the latest releases. Maybe I'll finish my to do
list in v0.8 . The most important items on the to do list are:
1) Two intefaces, one command line only & one GUI like now, you can
	choose this when loggin in.
2) Password encryption!

And further:
3) Redesign javascript part
4) Create one-function-to-rule-them-all so I can check which of the
	command execution methods work, this part is slowing down normal
	commands.
5) There is a large block of space used for the About, but it's kind
of unnecessary, can't find any other use for that.

And the to do stuff that probally won't make it:
6) Small pop up windows for:
		|Upload
		|Filebrowser
		|File Editor
7) Completely bug-free filebrowser & editor...sorry for this, but these
functions where kind of rushed, but were too handy to cut out.

If you have any suggestions, questions or feedback, you can e-mail me at
						ironfist99@gmail.com

	~Iron