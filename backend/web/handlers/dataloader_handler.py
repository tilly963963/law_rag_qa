import os
import json
import time
import logging
import falcon
from dataclasses import asdict
from web.handlers.abstract_handler import AbstractHandler
# from libs.vector_search import VectorSearch
from libs.parser_html import ParserHtml
# import pdfplumber
from libs.embedding import EmbModelCloud


logger = logging.getLogger(__name__)

try:
    import chromadb
except RuntimeError:
    import sys
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules["pysqlite3"]
    import chromadb


class DataLoaderController():
    def __init__(self, **kwargs):
        self.parser_model = ParserHtml()
        self.emb_model = EmbModelCloud()

    def wrapper(self, results):
        outs = {
            "predictions": {},
            "status": "ok",
        }
        for name, result in results.items():
            outs["predictions"][name] = {
                # "hits": [asdict(r) for r in result["res"]],
                # "time_sec": result["dt"],
               "hits":  result
            }
        return outs

    # def run(self, text, file_name, **kwargs):
    def run(self, uploaded_files_datas, **kwargs):

        window_size = 1000# kwargs["window_size"]
        stride = 0# kwargs["stride"]
        logger.info("uploaded_files_datas: {}".format(uploaded_files_datas))

        import pandas as pd
        import math


        data = []
        uploaddata={}
        for uploaded_files_data in uploaded_files_datas:
            file_name = uploaded_files_data.get('file_name')
            text = uploaded_files_data.get('text')
            text =text.replace(" ",'').replace("\n",'').replace(".",'')

                
            split_num = len(text)/ (window_size - stride)
            # file_data = {}
            logger.info("split_num: {}".format(split_num))

            for id,i in enumerate(range(math.ceil(split_num))):
                logger.info(" {}".format(id))
                file_data={}
                logger.info("{}, {}".format((window_size - stride)*i ,(window_size - stride)*i+window_size))
																																																																														
                file_data['file_name'] = file_name
                # file_data['is_upload_data'] =True
                
                file_data['article'] = text[(window_size - stride)*i : (window_size - stride)*i+window_size]
                file_data['article_emb'] = self.emb_model.encode(file_data['article'])
                file_data['meta'] = {'label':'upload_data','title':'no title','is_upload_data':True,'number':'pass'}
                file_data['id'] = id
                file_data['title'] = 'pass'
                file_data['number'] = 'pass'


                

                data.append(file_data)
            logger.info("data: {}".format(data))
            uploaddata['uploaddata']=data

        result = self.wrapper(uploaddata)
        logger.info("result: {}".format(result))

        return result

class DataLoader(AbstractHandler):
    handler_identifier = "data_index"

    def __init__(self, **kwargs):
        
        self.controller = DataLoaderController(**kwargs)

    def _on_post(self, req, res):
        logger.info("dataloder event: on_post, data: {}".format(req))
        
        uploaded_files_datas = req.context["data"].get('uploaded_files_data',[])

        if uploaded_files_datas == []:
            raise falcon.HTTPBadRequest("uploaded files is required")
      

        return self.controller.run(
            uploaded_files_datas
        )
