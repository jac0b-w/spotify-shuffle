I constantly see people complain about the spotify shuffle algorithm so here's my solution.<br>
This program shuffles your playlist completely randomly and creates a queue so you don't listen to the same songs over and over again.<br>
<br>
<ti>One time inital setup</ti><br>
Go to https://developer.spotify.com/dashboard/ <br>
Accept the terms and create an app for non-commercial use. You can call it whatever you like.<br>
Once you get to the dashboard click: settings > enter redirect url ```http://localhost/``` > set > save <br>
run spotify-shuffle.exe<br>
Copy the client id and client secret from the developer dashboard<br>
Press 'Sign In'<br>
You may be asked to sign in to spotify<br>
When you reach the "This site can’t be reached" page copy the url and enter it into the 'Redirect URL' box and press 'Authorise'<br>
Press shuffle to get a shuffled playlist queue<br>
<br>
If you want to run the .py file you need to install spotipy ```pip install spotipy```
