import logging
import asyncio
import opentracing
from functools import wraps
from sanic.response import json
from config import TOKEN
from logging.handlers import RotatingFileHandler


from sanic.handlers import ErrorHandler
from opentracing.ext import tags
from execption import CustomException

logger = logging.getLogger('sanic')
_log = logging.getLogger('zipkin')

PAGE_COUNT = 20

def log(level, message):

    logger = logging.getLogger('socket')

    #  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
    if not logger.handlers:
        log_name = 'socket.log'
        log_count = 2
        log_format = '%(asctime)s %(levelname)s %(module)s %(funcName)s-[%(lineno)d] %(message)s'
        log_level = logging.INFO
        max_bytes = 10 * 1024 * 1024
        handler = RotatingFileHandler(log_name, mode='a', maxBytes=max_bytes, backupCount=log_count)
        handler.setFormatter(logging.Formatter(log_format))
        logger.setLevel(log_level)
        logger.addHandler(handler)

    if level == 'info':
        logger.info(message)
    if level == 'error':
        logger.error(message)


def auth(token):
    def wrapper(func):
        @wraps(func)
        async def auth_token(req, *arg, **kwargs):
            try:
                value = req.headers.get(token)
                if value and TOKEN != value:
                    r = await func(req, *arg, **kwargs)
                    return json({'retcode': 0, 'stdout': r})
                else:
                    return json({'retcode': 1, 'stderr': 'status{}'.format(403)})
            except Exception as e:
                log('error', str(e))
                return json({'retcode': 1, 'stderr': str(e)})
        return auth_token
    return wrapper


def jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]

async def async_request(calls):
    results = await asyncio.gather(*[ call[2] for call in calls])
    for index, obj in enumerate(results):
        call = calls[index]
        call[0][call[1]] = results[index]

async def async_execute(*calls):
    results = await asyncio.gather(*calls)
    return tuple(results)

def id_to_hex(id):
    if id is None:
        return None
    return '{0:x}'.format(id)

async def consume(q, zs):
    async with aiohttp.ClientSession() as session:
        while True:
            # wait for an item from the producer
            try:
                span = await q.get()
                annotations = []
                binary_annotations = []
                annotation_filter = set()
                service_name = span.tags.pop('component') if 'component' in span.tags else None
                endpoint = {'serviceName': service_name if service_name else 'service'}
                if span.tags:
                    for k, v in span.tags.items():
                        binary_annotations.append({
                            'endpoint': endpoint,
                            'key': k,
                            'value': v
                        })
                for log in span.logs:
                    event = log.key_values.get('event') or ''
                    payload = log.key_values.get('payload')
                    an = []
                    start_time = int(span.start_time*1000000)
                    duration = int(span.duration*1000000)
                    if event == 'client':
                        an = {'cs': start_time,
                            'cr': start_time + duration}
                    elif event == 'server':
                        an = {'sr': start_time,
                            'ss': start_time + duration}
                    else:
                        binary_annotations["%s@%s" % (event, str(log.timestamp))] = payload
                    for k, v in an.items():
                        annotations.append({
                            'endpoint': endpoint,
                            'timestamp': v,
                            'value': k
                        })
                span_record = create_span(
                    id_to_hex(span.context.span_id),
                    id_to_hex(span.parent_id),
                    id_to_hex(span.context.trace_id),
                    span.operation_name,
                    start_time,
                    duration,
                    annotations,
                    binary_annotations,
                )
                if zs:
                    async with session.post(zs, json=[span_record]) as res:
                        logger.info(await res.text())
                _log.info("{} span".format(service_name), span_record)
                q.task_done()
            except RuntimeError as e:
                logger.errro(e)
                break
            except Exception as e:
                logger.error("{}".format(e))
                raise e
            finally:
                pass

class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        if isinstance(exception, CustomException):
            data = {
                'message': exception.message,
                'code': exception.code,
            }
            if exception.error:
                data.update({'error': exception.error})
            span = request['span']
            span.set_tag('http.status_code', str(exception.status_code))
            span.set_tag('error.kind', exception.__class__.__name__)
            span.set_tag('error.msg', exception.message)
            return json(data, status=exception.status_code)
        return super().default(request, exception)

def before_request(request):
    try:
        span_context = opentracing.tracer.extract(
            format=opentracing.Format.HTTP_HEADERS,
            carrier=request.headers
        )
    except Exception as e:
        span_context = None
    handler = request.app.router.get(request)
    span = opentracing.tracer.start_span(operation_name=handler[0].__name__,
                             child_of=span_context)
    span.log_kv({'event': 'server'})
    span.set_tag('http.url', request.url)
    span.set_tag('http.method', request.method)
    ip = request.ip
    if ip:
        span.set_tag(tags.PEER_HOST_IPV4, "{}:{}".format(ip[0], ip[1]))
    return span

def create_span(span_id, parent_span_id, trace_id, span_name,
                start_time, duration, annotations,
                binary_annotations):
    span_dict = {
        'traceId': trace_id,
        'name': span_name,
        'id': span_id,
        'parentId': parent_span_id,
        'timestamp': start_time,
        'duration': duration,
        'annotations': annotations,
        'binaryAnnotations': binary_annotations
    }
    return span_dict




