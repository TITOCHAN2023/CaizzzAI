import requests
from env import TTS_URL
import os
from logger import logger


def tts(uid:int,content:str, voicename:str="Person1",tts_class:str="F5-TTS"):
    if content=="":
        logger.error("text is empty")
        return 
    

    '''F5-TTS'''
    if tts_class=="F5-TTS":
        url = TTS_URL[0]
        requestsdata = {
                    "voicename": voicename,
                    "content": content,
                }
        response = requests.post(url, data=requestsdata)
        
        if response.status_code == 200:
            jsonresponse1 = response.json()
            audio_url = jsonresponse1['url']

            response = requests.get(audio_url)
            audio_name=audio_url.split("/")[-1]

            if response.status_code == 200:
                os.makedirs(f"audio_output/{uid}", exist_ok=True)
                with open(f"audio_output/{uid}/{audio_name}", "wb") as f:
                    f.write(response.content)
                return audio_name
            
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return 
    else:
        logger.error("Invalid TTS class")
        return 
    
    