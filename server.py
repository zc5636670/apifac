# author Chaos
import os

from flask import jsonify
from flask import Flask
from flask import request
from flask_cors import CORS

__all__ = ['GetServer', 'PostServer', 'ApiServer']


class RequestMethod(object):
    def __init__(self, url_rule, func, method_type):
        self.url_rule = url_rule
        self.func = func
        self.method_type = method_type

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)

    def response(self, *args, **kwargs):
        content, code = '', 200
        try:
            content = self.func(*args, **kwargs)
            if isinstance(content, str):
                return content, code
            if isinstance(content, dict) or isinstance(content, list):
                return jsonify(content), 200
        except Exception as e:
            result = str(e)
            return jsonify(dict(err_msg=result)), 500


class GetServer(RequestMethod):
    def __init__(self, name, func):
        super(GetServer, self).__init__(name, func, 'GET')


class PostServer(RequestMethod):
    def __init__(self, name, func):
        super(PostServer, self).__init__(name, func, 'POST')


class ApiServerMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'ApiServer':
            return type.__new__(mcs, name, bases, attrs)
        mappings = dict()
        for k, v in attrs.items():
            if issubclass(type(v), RequestMethod):
                mappings[k] = v
        attrs['urls'] = mappings
        for k in mappings.keys():
            attrs.pop(k)
        return type.__new__(mcs, name, bases, attrs)


class ApiServer(object, metaclass=ApiServerMeta):
    def __init__(self, name, url_prefix="", flask_name=__name__):
        self.name = name
        self.url_prefix = url_prefix
        self.app = Flask(flask_name)
        self.init_urls()

    def init_urls(self):
        for k, v in self.urls.items():
            self.app.add_url_rule(os.path.join('/', self.url_prefix, self.name, v.url_rule),
                                  view_func=v.response,
                                  endpoint="%s.%s" % (self.name, k),
                                  methods=[v.method_type])
        CORS(self.app, resources=r'/api/*')

    def export_json(self):
        pass

    def export_python(self):
        pass


#  ####### 以下为测试代码$##########3
def hello_word():
    name = request.args.get('name', None)
    return {"content": 'Hello {}!'.format(name)}


def post_data():
    data = request.json.get('html', '')
    return {}


def routes():
    pass


class ApiTestServer(ApiServer):
    hello = GetServer('hello', hello_word)
    post_data = PostServer('post', post_data)


api = ApiTestServer('test', url_prefix="api")
app = api.app

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=15000)
