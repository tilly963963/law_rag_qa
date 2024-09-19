import os
import json
import time
import logging
import falcon
from dataclasses import asdict
from web.handlers.abstract_handler import AbstractHandler
from libs.vector_search import VectorSearch

from libs.embedding import EmbModelCloud
from libs.llm import LLM_NAME

logger = logging.getLogger(__name__)


class SearchController():
    def __init__(self):
        self.emb_model = EmbModelCloud()
        models = [
            VectorSearch(model_name=LLM_NAME),
        ]
        logger.info("vectorSearch(model_name=LLM_NAME): {}".format(LLM_NAME))

        self.models = {m.get_name(): m for m in models}
        self.algos = list(self.models.keys())
        logger.info("search engine models: {}".format(self.algos))

    def wrapper(self, results):
        outs = {
            "predictions": {},
            "status": "ok",
        }
        for name, result in results.items():
            outs["predictions"][name] = {
                "hits": [asdict(r) for r in result["res"]],
                "time_sec": result["dt"],
            }
        return outs

    def run(self, sentence, **kwargs):

        label_by = kwargs["label_by"]
        file_by = kwargs["file_by"]
        uploaddata = kwargs["uploaddata"]
        mergedata = kwargs["mergedata"]
        model_name = kwargs["model_name"]


        t1 = time.time()
        if LLM_NAME == 'gpt-4o':
            q_emb = self.emb_model.encode(sentence)
        else:
            q_emb = self.emb_model.local_encode(sentence) 
        qt = round(time.time() - t1, 4)
        logger.info("LLM_NAME {} ".format(LLM_NAME))
        logger.info("sentence q_emb {}  ".format(len(q_emb)))

        results = {}

        for name, model in self.models.items():
            t1 = time.time()
            logger.info("seasearch_files: uploaddata {}  mergedata {}".format(uploaddata, mergedata))
            logger.info("seasearch_files: label_by {}  file_by {}".format(label_by, file_by))

            if mergedata:
                res = model.search_files(
                    sentence,
                    label_by=label_by,
                    file_by=file_by,
                    q_emb=q_emb,
                    uploaddata=uploaddata,
                    model_name=model_name
                )
            elif uploaddata:#clean label_by & file_by
                logger.info("search_uploaddata: {}".format(uploaddata))

                res = model.search_uploaddata(
                    sentence,
                    label_by=label_by,
                    file_by=file_by,
                    q_emb=q_emb,
                    uploaddata=uploaddata
                )
            else:
                logger.info("search uploaddata: {}".format(uploaddata))

                res = model.search(
                    sentence,
                    label_by=label_by,
                    file_by=file_by,
                    q_emb=q_emb,
                    model_name=model_name
                )
            
            dt = round(time.time() - t1, 4)
            if model.need_emb():
                dt += qt
            results[name] = {"res": res[:10], "dt": dt}
        outputs = self.wrapper(results)
        return outputs


class SearchHandler(AbstractHandler):
    handler_identifier = "pycon_law_rag"

    def __init__(self, **kwargs):
        self.emb_model = EmbModelCloud()
        self.controller = SearchController(**kwargs )

    def _on_get(self, req, res):
        sentence = req.get_param("sentence", required=True)
        logger.info("sentence: {}".format(sentence))
        query_by = req.get_param("query_by", [])
        filter_by = req.get_param("filter_by", [])
        institution_by = req.get_param("institution_by", [])
        file_by = req.get_param("file_by", [])

        if sentence == "":
            raise falcon.HTTPBadRequest("sentence is required")

        args = {"query_by": query_by, "filter_by": filter_by, "institution_by": institution_by,"file_by":file_by}
        return self.controller.run(sentence, **args)

    def _on_post(self, req, res):
        # logger.info("event: on_post, data: {}".format(req.context["data"]))


        ## 取出所有參數
        # 用戶輸入的搜尋句
        sentence = req.context["data"].get("sentence", "")
       
        label_by = req.context["data"].get("label", [])
        # 指定的類別
        file_by = req.context["data"].get("file", [])
        uploaddata = req.context["data"].get("uploaddata", {})
        mergedata = req.context["data"].get("mergedata", bool)
        # model_name = req.context["data"].get("model_name", "")

        if sentence == "":
            raise falcon.HTTPBadRequest("sentence is required")

        return self.controller.run(
            sentence,
            label_by=label_by,
            file_by=file_by,
            uploaddata=uploaddata,
            mergedata=mergedata,
            model_name=LLM_NAME
            # query_emb=query_emb
        )
