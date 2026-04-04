import requests
import json
from itertools import islice

import os
from dotenv import load_dotenv

# API Key is saved in .env file
load_dotenv(dotenv_path = "./.env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "TaylorSwift"

maxResults = 50

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

        response.raise_for_status()
        
        data = response.json()
        # print(json.dumps(data,indent=4))

        # Path to required data in json(video_stats.json - eg)
        channel_items = data["items"][0]
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        # print(channel_playlistId)
        return channel_playlistId
    
    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlistId):

    video_ids = []

    pageToken = None 

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"
            
            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item["contentDetails"]['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e




def extract_video_data(video_ids):

    extracted_data = []

    def batch_list(video_ids):
        # Create an iterator
        it = iter(video_ids)

        # Use islice to generate chunks of size defined in maxResult
        batches = []
        for _ in range(0, len(video_ids), maxResults):
            batches.append(list(islice(it, maxResults)))

        return batches
    
    try:

        for batch in batch_list(video_ids):
            
            video_ids_batch = ",".join(batch)

            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={video_ids_batch}&key={API_KEY}'

            response = requests.get(url)
            response.raise_for_status()
                
            data = response.json()
            # print(json.dumps(data,indent=4))

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']
            
                video_data = {
                    'video_id' : video_id,
                    'title' : snippet['title'],
                    'publishedAt' : snippet['publishedAt'],
                    'duration' : contentDetails['duration'],
                    'viewCount' : statistics.get('viewCount', None),            #using get to handle cases where the author hides views, likes, or comments and the API returns inconsistent data.
                    'likeCount' : statistics.get('likeCount', None),
                    'commentCount' : statistics.get('commentCount', None),
                }

                extracted_data.append(video_data)
        return extracted_data 
            

            # data['items'][0]['snippet']['title'],
            # data['items'][0]['snippet']['publishedAt'],
            # data['items'][0]['contentDetails']['duration'],
            # data['items'][0]['statistics']['viewCount'],
            # data['items'][0]['statistics']['likeCount'],
            # data['items'][0]['statistics']['commentCount']
    
    except requests.exceptions.RequestException as e:
        raise e
    

if __name__ == "__main__":

    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)

    extracted_data = extract_video_data(video_ids)
    print(len(extracted_data))      # should be equal to no. of videos posted by the channel
    