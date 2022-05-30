# slack-bot
Slack bot that automatically uploads media files to google drive, without running on a server. 

# How it works.

This bot runs continuously with a while true loop every 5 seconds. In each iteration, he gets the last message sent by each channel we've told him to monitor and check if it contains a file. If it contains files then for each of them, he downloads it and uploads it to the corresponding google drive folder. If everything goes well, he sends a success message to the channel.

To run, we do not need tools that expose local server ports to the Internet, such as ngrok.
