import os
from slack import WebClient
from slack.errors import SlackApiError
from pathlib import Path
from dotenv import load_dotenv
import time
import requests
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import datetime

env_path = Path('.') / '.env' #path for our .env file
load_dotenv(dotenv_path=env_path)
client = WebClient(token=os.environ['SLACK_TOKEN'])
conversation_history = []
channel_id = [] #array with all the channels we want to listen to. Ex ['id1', 'id2']

ids = [] #array for keeping the id's of the files we found in on channel. We need this to be an array in case someone has upload more that one file in one message.

newID = ""

folders = [] #array with all the google drive folders. Ex ['f1', 'f2']

gauth = GoogleAuth() #google auth.
drive = GoogleDrive(gauth)

oldFile = "" #Save the name of the last file so we can delete it, locally , after sending it to google drive.
nameOfFile = "" #the name of the file we found in one of the channels we listen to.

while True: #Run forever
    for i in range(len(channel_id)):
        ids.clear() #Clear ids array
        try:
            result = client.conversations_history(channel=channel_id[i]) 

            conversation_history = result["messages"][0] #get the last message of the channel

            if "files" in conversation_history: #if we found a file in the message
                print(len(conversation_history["files"])) #prind the number of the files

                filesCounter = len(conversation_history["files"]) #store the number

                for y in range(filesCounter): #for all the files 
                    newID = conversation_history["files"][y]["id"] #store the id of the file

                    if newID not in ids: #if this is true it, means that we have not upload the file yet.
                        url = conversation_history["files"][y]["url_private_download"] #get the url of the file

                        response = requests.get(url, headers={'Authorization': 'Bearer %s' % os.environ['SLACK_TOKEN']},
                                                stream=True) #Send a request with the slack token.
                        response.raw.decode_content = True

                        nameOfFile = conversation_history["files"][y]["name"] #store the name of the file

                        # Open a local file with wb ( write binary ) permission.
                        with open(str(nameOfFile), 'wb') as f: #Download the file locally
                            shutil.copyfileobj(response.raw, f)

                        print('File successfully Downloaded: ', nameOfFile)
                        #Create a google drive file and uploade it
                        fileUpload = drive.CreateFile({'parents': [{'id': folders[i]}], 'title': nameOfFile}) 
                        fileUpload.SetContentFile(nameOfFile)
                        fileUpload.Upload()

                        text = "Files successfully Uploaded to Google Drive " + str(datetime.datetime.now())
                        print(text)

                        f.close()

                        try:   #remove the local file
                            os.remove(oldFile)
                        except OSError as o:
                            print(o)
                            f = open('log.txt', 'w')
                            f.write('An exceptional thing happen - %s' % o)
                            f.close()

                    oldFile = nameOfFile

                client.chat_postMessage(channel=channel_id[i], text=text) #Write to channel.

        except SlackApiError as e:
            print(e)
            f = open('log.txt', 'w')
            f.write('An exceptional thing happened - %s' % e + str(time.time()) + "\n")
            f.close()

    time.sleep(5)#repeat every 5 sec


