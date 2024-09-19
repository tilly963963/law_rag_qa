import os
import time
import logging
import falcon
import tiktoken
from dataclasses import asdict
from web.handlers.abstract_handler import AbstractHandler
from libs.llm import QA_SYS_MSG, QA_SYS_WHOLE_RULE, LLM_NAME


logger = logging.getLogger(__name__)
TOKEN_LIMIT = 128000-4096

class QAController():
    def __init__(self, *, llm_model, intent_controller):
        logger.info("__init__")
        self.llm_model = llm_model
        self.controller = intent_controller
        if LLM_NAME=="gpt-4o":
            self.encoder = tiktoken.encoding_for_model(LLM_NAME)

    def get_msg_from_snippets(self, query, model, snippets, full_title_texts):#, sort_by=None):
        data = []
  
        for i, idx in enumerate(snippets):
            row = model.get_row(idx)
            fn = row["file_name"]
            title = row["title"]
            article = row["article"]
            full_title_text = full_title_texts[i]

            data.append((idx, fn, title, article, full_title_text))

    

        msg = "以下是法規知識庫的資料，法規知識庫的資料是由數個與問題相關的法規知識點組成，當中的法規知識點是依照相關性排序，與問題越相關的知識點排在越前面：\n```\n"
        for i, d in enumerate(data):
            idx, fn, title, article, full_title_text = d
        
            msg += f"***排序第{i+1}名相關的法規知識點***：\n"
            # msg += f"法規來源：\n"
            if title == 'pass':
                msg += f"法規名稱：{fn}\n"

            else:
                title =title.replace(' ','' )
                msg += f"法規名稱：{fn}\n"
                msg += f"法規章節：{title}\n"
            msg += f"法規內容：\n"

            msg += f"{full_title_text}\n\n"
        
        msg += f"```\n\n問題：{query}\n\n"+"""
注意事項：
1. 根據法規知識庫資料與問題提供“答案”和“法規來源”，“答案”是指法規知識庫中與問題最相關的法條內容;“法規來源”是指其對應的法規名稱、法規章節、完整法條。
2. “答案”與“法規來源”不允許編造。如果無法從法規知識庫資料得到答案，請回答“無法得知答案，請您重新提問”。
3. 回答請使用繁體中文
4. 回答請注意排版"""
    
        if LLM_NAME =='gpt-4o':
            tokens = self.encoder.encode(msg + QA_SYS_MSG)
            logger.info(f"Count Token. fn: {fn} tokens: {len(tokens)}")
            logger.info(f"len characters. fn: {fn} tokens: {len(msg + QA_SYS_MSG)}")
        #  Count Token. fn: 勞動基準法 tokens: 9811
        #  len characters. fn: 勞動基準法 tokens: 10698
        return msg

    def run(self, sentence, algorithm, snippets, filename, full_title_texts):
        model = self.controller.models[algorithm]
        snippets = [int(i) for i in snippets]
        # sorted_snippets=snippets[:5]
        msg = self.get_msg_from_snippets(sentence, model, snippets, full_title_texts)

        texts = [model.get_text(i) for i in snippets][0]
        t1 = time.time()     

        logger.info(f" msg {msg}")
        if LLM_NAME == 'gpt-4o':
            ans = self.llm_model.qa(QA_SYS_MSG, msg)
        else:
            ans = self.llm_model.ollama_qa(QA_SYS_MSG, msg)
        

        dt = round(time.time() - t1, 2)
     

        outputs = {
            "context": msg,
            "query": sentence,
            "response": ans.replace('```','\n').replace("###",'\n'),
            "index": snippets,
            "dt": dt,
            "algo": algorithm,
        }
        return outputs


class QAHandler(AbstractHandler):
    handler_identifier = "poc_docqa"

    def __init__(self, **kwargs):
        self.controller = QAController(**kwargs)

    def _on_get(self, req, res):
        sentence = req.get_param("sentence", required=True)
        algorithm = req.get_param("algorithm", required=True)
        snippets = req.get_param("snippets", required=True)
        filename = req.get_param("filename", required=True)

        logger.debug("sentence: {}. algorithm: {}. snippets: {}. filename: {}".format(
                sentence, algorithm, snippets, filename
            )
        )

        if sentence == "":
            raise falcon.HTTPBadRequest("sentence is required")
        try:
            snippets = [int(i) for i in snippets.split(",")]
        except:
            raise falcon.HTTPBadRequest("snippets not valid")

        return self.controller.run(sentence, algorithm, snippets, filename)

    def _on_post(self, req, res):

        sentence = req.context["data"].get("sentence", "")
        algorithm = req.context["data"].get("algorithm", "")
        snippets = req.context["data"].get("snippets", [])
        filename = req.context["data"].get("filename", "")
        full_title_texts = req.context["data"].get("full_title_texts", [])

        if sentence == "":
            raise falcon.HTTPBadRequest("sentence is required")

        if not algorithm:
            raise falcon.HTTPBadRequest("algorithm is required")

        if not snippets:
            raise falcon.HTTPBadRequest("snippets is required")

        return self.controller.run(sentence, algorithm, snippets, filename, full_title_texts)
