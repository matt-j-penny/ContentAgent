-- Opens one storyboard in the default browser, starting its local server if needed. No Terminal window.
-- Fill KIT, BOARD and PORT, then: osacompile -o "<Video> Storyboard.app" launcher.applescript
-- ponytail: one board per port, give each video's app its own port
property kit : "KIT"
property board : "BOARD"
property boardPort : "PORT"

on isUp(boardURL)
	try
		do shell script "/usr/bin/curl -fs --max-time 4 " & quoted form of (boardURL & "api/version")
		return true
	on error
		return false
	end try
end isUp

on run
	set boardURL to "http://localhost:" & boardPort & "/"
	set logFile to (POSIX path of (path to library folder from user domain)) & "Logs/storyboard-" & boardPort & ".log"
	if not isUp(boardURL) then
		do shell script "export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH; nohup python3 " & quoted form of kit & " serve " & quoted form of board & " " & boardPort & " > " & quoted form of logFile & " 2>&1 < /dev/null &"
		repeat 60 times
			if isUp(boardURL) then exit repeat
			delay 0.25
		end repeat
	end if
	if isUp(boardURL) then
		do shell script "/usr/bin/open " & quoted form of boardURL
	else
		activate
		display alert "The storyboard could not start" message "Details are in " & logFile
	end if
end run
