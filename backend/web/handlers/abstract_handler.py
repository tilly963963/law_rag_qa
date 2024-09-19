# Abstract Handler
# Author: Yen-chi Chen

import logging
import json
import falcon
import web.hook
from falcon import Request, Response
from functools import wraps
from schema import SchemaError

logger = logging.getLogger(__name__)


def wrap_return(func):
    # see why wraps: https://docs.python.org/3/library/functools.html#functools.wraps
    @wraps(func)
    def wrapper(self, req: Request, res: Response, *params):
        try:
            result = func(self, req, res, *params)
            result = json.dumps(result, ensure_ascii=False, sort_keys=True)
        except SchemaError as e:
            logger.exception(e)
            res.body = json.dumps({"status": "error", "message": "Schema error: " + str(e)})
            res.status = falcon.HTTP_400
            return
        except falcon.HTTPError as e:
            logger.exception(e)
            res.body = json.dumps({"status": "error", "message": e.title})
            res.status = e.status
            logger.info(f" !!! {e.title}")

            return
        except Exception as e:
            logger.exception(e)
            res.body = json.dumps({"status": "error", "message": "Internal Server Error"})
            res.status = falcon.HTTP_500
            return

        res.body = result
        res.status = falcon.HTTP_200
    return wrapper


class AbstractHandler(object):
    def _on_get(self, req: Request, res: Response):
        raise falcon.HTTPNotFound(title="no GET method")

    def _on_post(self, req: Request, res: Response):
        raise falcon.HTTPNotFound(title="no POST method")

    @wrap_return
    def on_get(self, req: Request, res: Response, *params):
        return self._on_get(req, res, *params)

    @falcon.before(web.hook.json_body)
    @wrap_return
    def on_post(self, req: Request, res: Response, *params):
        return self._on_post(req, res, *params)

