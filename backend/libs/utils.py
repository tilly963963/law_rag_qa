from openai import OpenAI
from config import KEY_FILE

def synonyms_normalize(s):
    s = s.replace("台", "臺")
    return s


class OpenAIClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with open(KEY_FILE) as fr:
                key = fr.read()
            cls._instance = OpenAI(api_key=key)
        return cls._instance

openai_client = OpenAIClient()
