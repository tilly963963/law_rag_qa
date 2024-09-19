import logging
import datetime

logger = logging.getLogger(__name__)


class LoggingMiddleware(object):
    def process_request(self, req, resp):
        req.context['request_begin_datetime'] = datetime.datetime.now()

        logger.info("event: request_begin, {} {} ({})".format(req.method, req.uri, req.remote_addr))

    def process_response(self, req, resp, resource, params):
#        logger.info("event: output: {}".format(resp.body))
        logger.info("event: request_span, diff: {}".format(datetime.datetime.now() - req.context['request_begin_datetime']))
