# ListenToThisPlaylist

A simple PRAW script that allows you to discover new music through
[/r/listentothis](https://reddit.com/r/listentothis) or any subreddits you
like.

# Usage

1. Register a script-type application with your reddit account, this can be
   done [here](https://www.reddit.com/prefs/apps/).
2. Create a file called `app.json` and fill it out, following this template:

```json
{
    "client_id": "{The id of your application, can be seen at the top.}",
    "client_secret": "{The client secret of your application.}",

    "username": "{Your reddit username}",
    "password": "{Your reddit password}",

    "user_agent": "{your os name}:ListenToThisPlaylist:v1.0.0 (by /u/{your username})"
}
```

3. Run `pip3 install -r requirements.txt` to download the needed dependencies.
4. Run `python3 app.py` whenever you want to listen to music!
