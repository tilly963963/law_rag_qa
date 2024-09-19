import os
import logging
import falcon
from web.middleware import LoggingMiddleware
from web.handlers.parser_handler import ParserHandler
from web.handlers.file_handler import FileHandler
from web.handlers.search_handler import SearchHandler
from web.handlers.dataloader_handler import DataLoader
from web.handlers.qa_handler import QAHandler

from libs.llm import LLMModelCloud as LLMModel

from libs.parser_html import ParserHtml

import requests

def init_logging():
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(processName)s --- [%(threadName)s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")

    logger_level = int(os.getenv("LOGGER_LEVEL", logging.INFO))
    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)

    handlers = [ch]

    logging.basicConfig(level=logger_level, handlers=handlers)


def disable_auto_parse_qs_csv(app):
    app.req_options.auto_parse_qs_csv = False


# init logging system
init_logging()

# init API server from falcon
api = falcon.API(middleware=[LoggingMiddleware()])
disable_auto_parse_qs_csv(api)


class home:
    def on_get(self, req, resp):
        resp.text = "ok"
        resp.status = falcon.HTTP_200

# emb_model = EmbModel()
llm_model = LLMModel()

intent_handler = ParserHandler()
file_handler = FileHandler()
search_handler = SearchHandler()
dataloader_handler = DataLoader()
api.add_route("/", home())
api.add_route("/url", intent_handler)
api.add_route("/file", file_handler)
api.add_route("/dataloader", dataloader_handler)
api.add_route("/search", search_handler)
api.add_route("/llm", QAHandler(
    llm_model=llm_model,
    intent_controller=search_handler.controller
))