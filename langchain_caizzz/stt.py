from openai import OpenAI
from logger import logger
from env import OPENAI_BASE_URL,OPENAI_API_KEY

def stt(stt_name: str, audio_file:str,api_key: str, base_url: str = "",stt_class:str="openai", **kwargs)-> str:
    """STT."""

    if stt_class == "openai":
        if base_url=="":
            base_url=OPENAI_BASE_URL
        if stt_name=="":
            stt_name="whisper-1"
        logger.info(f"Init OpenAI STT: {stt_name},base_url:{base_url}")
        stt = OpenAI(
            base_url=base_url,
            api_key=api_key,
            **kwargs,
        )
        transcription = stt.audio.translations.create(
            model=stt_name,
            file=open(audio_file, "rb"),

        )
        return transcription.text

    
def main():
    test_text=stt(stt_name="whisper-1",audio_file="audio_input/test.MP3",api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL)

    print(test_text)

if __name__ == "__main__":
    main()