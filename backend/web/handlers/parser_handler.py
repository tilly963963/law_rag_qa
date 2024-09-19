import os
import json
import time
import logging
import pandas as pd
import falcon
from dataclasses import asdict
from web.handlers.abstract_handler import AbstractHandler
from libs.parser_html import ParserHtml


logger = logging.getLogger(__name__)


class ParserController():
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
                "hits": result
            }
        return outs

    def run(self, urls, **kwargs):

        urls_data={}
        for url in urls:
            parser_url_data = self.parser_model.get_url_data(url)
            urls_data[url]=parser_url_data
    
        result = self.wrapper(urls_data)

        return result

class ParserHandler(AbstractHandler):
    handler_identifier = "data_index"

    def __init__(self, **kwargs):
        self.controller = ParserController(**kwargs)

    def _on_post(self, req, res):
        logger.info("event: on_post, data: {}".format(req.context["data"]))

        ## 取出所有參數
        # 用戶輸入的搜尋句
        urls = req.context["data"].get("url", "")
        # 要搜尋的欄位，預設搜尋段落
        # query_by = req.context["data"].get("query_by", ["text"])
        # # 指定的類別
        # filter_by = req.context["data"].get("filter_by", [])
        # # 指定主管機關
        # institution_by = req.context["data"].get("institution_by", [])

        # file_by = req.context["data"].get("file_by", [])

        if urls == "":
            raise falcon.HTTPBadRequest("sentence is required")

        return self.controller.run(
            urls,
        
        )

   