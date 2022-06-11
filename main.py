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

env_path = Path('.') / '.env' #path for our .env file
load_dotenv(dotenv_path=env_path)
client = WebClient(token=os.environ['SLACK_TOKEN'])


gauth = GoogleAuth() #google auth.
drive = GoogleDrive(gauth)

googleDriveFolders = ['', '', ''] # google drive forders id's
slackChannels = ['', '', ''] # slack channels id's

driveArrayIds = [] # images already on the forders

# get all the id's of the files in the forlders
def googleDriveFiles(id):
  driveFolder = "'%s' in parents and trashed=false" % googleDriveFolders[id]
  fileList = drive.ListFile({'q': driveFolder}).GetList()
  for file in fileList:
    driveArrayIds.append(file['title'])
  return driveArrayIds

# get hte slack files from the messages on the.
def slackFiles(driveArrayIdsm, id):
  result = client.conversations_history(channel=slackChannels[id])
  for i in range(len(result['messages'])):
    if "files" in result['messages'][i]:
      for y in range(len(result['messages'][i]['files'])):
        if result['messages'][i]['files'][y]['name'] not in driveArrayIds:

          print(result['messages'][i]['files'][y]['name'])
          url = result['messages'][i]['files'][y]['url_private_download']

          response = requests.get(url, headers={'Authorization': 'Bearer %s' % os.environ['SLACK_TOKEN']},stream=True)
          response.raw.decode_content = True

          nameOfFile = result['messages'][i]['files'][y]['name']

          with open('media/' + str(nameOfFile), 'wb') as f: #Download the file locally
            shutil.copyfileobj(response.raw, f)
          
          fileUpload = drive.CreateFile({'parents': [{'id': googleDriveFolders[id]}], 'title': nameOfFile}) 
          fileUpload.SetContentFile('./media/' + nameOfFile)
          fileUpload.Upload()

if __name__ == '__main__':
  while True:
    for id in range(len(googleDriveFolders)):
      slackFiles(googleDriveFiles(id), id)
    # delete the files on the folder
    folder = './media'
    for filename in os.listdir(folder):
      file_path = os.path.join(folder, filename)
      try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
      except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))
    driveArrayIds = []
    time.sleep(30)
