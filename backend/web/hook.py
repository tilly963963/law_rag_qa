import json
import logging

logger = logging.getLogger(__name__)

def json_body(req, response, resource, params):
    if req.content_length:
        try:
            data = req.stream.read().decode('utf-8')
            data = json.loads(data)

            req.context['data'] = data
        except:
            req.context['data'] = {}
    else:
        req.context['data'] = {}
        logger.info("req.context['data'] {}".format(req.context['data']))


def req_params_to_data(req, response, resource, params):
    """將 GET 的 params 放入 req.context['data'] 中
    """
    try:
        data = req.params
    except:
        data = {}
    req.context['data'] = data
