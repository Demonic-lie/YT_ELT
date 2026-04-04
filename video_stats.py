import requests
import json

import os
from dotenv import load_dotenv

# API Key is saved in .env file
load_dotenv(dotenv_path = "./.env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "TaylorSwift"

def get_playlist_id():

    try:  

        # setting the url for API call
        url = "https://youtube.googleapis.com/youtube/v3/channels"

        # setting the parameters of url
        param = {
            "part" : "contentDetails",
            "forHandle" : CHANNEL_HANDLE,
            "key" : API_KEY
        }
        # print(API_KEY)

        response = requests.get(url, params=param)
        # print(response)

        data = response.json()
        # print(json.dumps(data,indent=4))

        # Path to required data in json(video_stats.json - eg)
        channel_items = data["items"][0]
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        # print(channel_playlistId)
        return channel_playlistId
    
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    get_playlist_id()