 I constantly see people complain about the spotify shuffle algorithm so here's my solution.<br>
This program shuffles your playlist completely randomly and creates a queue so you don't listen to the same songs over and over again.<br>
<br>
Go to https://developer.spotify.com/dashboard/ <br>
Create an app<br>
Go to settings and add ```http://localhost/``` as a redirect url <br>
run spotify-shuffle.exe<br>
Copy the client id and client secret and paste them into the entry boxes<br>
Press authorise<br>
You may be asked to sign in to spotify<br>
When you reach the "This site can’t be reached" page copy the url and enter it into the console<br>
Press shuffle to get a shuffled playlist queue<br>
<br>
If you want to run the .py file you need to install spotipy ```pip install spotipy```
