import os
import json
import time
import logging
import falcon
from dataclasses import asdict
from web.handlers.abstract_handler import AbstractHandler
# from libs.vector_search import VectorSearch
from libs.parser_html import ParserHtml

logger = logging.getLogger(__name__)


class FileController():
    def __init__(self, **kwargs):
      
        self.parser_model = ParserHtml()
   
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

    def run(self, file_data,save_filename, **kwargs):
        import pandas as pd

        article_datas={}
        law_datas={}
        num=0
        count=0
        for url, datas in file_data.items(): 
            for file_name, data in datas['hits'].items(): 
                # if isinstance (data['link'],str) :
                    
                    article_data = self.parser_model.get_article(file_name, data)
                    if article_data is not None:
                        article_datas[file_name]=article_data
            count=count+1
      
        for k,v in article_datas.items():
            for data in v:
                num=num+1
                law_datas[num]=data


        law_link_df = pd.DataFrame(law_datas).T
        law_link_df.to_csv('{}.csv'.format(save_filename), encoding="utf-8-sig")
        law_link_df.to_excel('{}.xlsx'.format(save_filename))

        result = self.wrapper(article_datas)
        logger.info("result: {}".format(result))

        return result

class FileHandler(AbstractHandler):
    handler_identifier = "data_index"

    def __init__(self, **kwargs):
        
        self.controller = FileController(**kwargs)

    def _on_post(self, req, res):
   
        logger.info("event: on_post, data: {}".format(req.context["data"]))

        ## 取出所有參數
        # 用戶輸入的搜尋句
        file_data = req.context["data"].get("file_data", "")
        save_filename = req.context["data"].get("save_filename", "")


        if file_data == "":
            raise falcon.HTTPBadRequest("sentence is required")

        return self.controller.run(
            file_data,
            save_filename,
       
        )
