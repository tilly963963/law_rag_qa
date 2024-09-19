import logging
import falcon
import os
import openai
from config import KEY_FILE
from FlagEmbedding import BGEM3FlagModel

def synonyms_normalize(s):
    s = s.replace("台", "臺")
    return s

api_key = ""

from openai import OpenAI
client = OpenAI(api_key = api_key)
 

logger = logging.getLogger(__name__)
# OpenAI
class EmbModelCloud:
    def __init__(self):
        logger.info("Use cloud embedding model!")

        self.local_model = BGEM3FlagModel('./models_bag_m3',
                            use_fp16=True)
    def encode(self, text) -> list:
        logger.info("KEY_FILE = {}".format(KEY_FILE))

        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-large",
            )
            e = response.data[0].embedding
        except Exception as e:
            logger.exception(e)
            raise falcon.HTTPServiceUnavailable("Embedding API is not available.")
        return e

    def local_encode(self, text):
        logger.info("local_encode")
        
        emb = self.local_model.encode(text)['dense_vecs']
        # emb = local_model.encode(text, return_dense=True, return_sparse=True, return_colbert_vecs=False)
        return emb.tolist()
