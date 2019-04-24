# author Chaos
import os
import json

import requests

__all__ = ['ApiFacError', 'GetClient', "PostClient", "ApiClient"]


class ApiFacError(Exception):
    def __init__(self, err_msg, status_code):
        self.err_msg = err_msg
        self.code = status_code


class MethodClient(object):
    def __init__(self, name):
        self.name = name
        self.host = None
        self.port = None
        self.url_prefix = None
        self.use_ssl = False

    def init_host_port(self, host, port, url_prefix, use_ssl=False):
        self.host = host
        self.port = port
        self.url_prefix = url_prefix
        self.use_ssl = use_ssl

    @property
    def url(self):
        if self.use_ssl:
            http = 'https://'
        else:
            http = 'http://'
        url = "{}{}:{}{}".format(http, self.host, self.port, os.path.join('/', self.url_prefix, self.name))
        return url

    def _request(self, params={}, data={}):
        raise NotImplemented

    def __call__(self, params={}, data={}):
        try:
            result = self._request(params=params, json=data)
            if not result.status_code == 200:
                raise ApiFacError(result.content, result.status_code)
            return json.loads(result.text)
        except ApiFacError as e:
            raise e
        except Exception as e:
            raise ApiFacError("requests报错：{}".format(str(e)), 599)


class GetClient(MethodClient):
    def _request(self, params={}, json={}):
        return requests.get(self.url, params=params, data=json)


class PostClient(MethodClient):
    def _request(self, params={}, json={}):
        return requests.post(self.url, params=params, data=json)


class ApiClientMeta(type):
    def __new__(mcs, name, bases, attrs):
        # 下面的名字一定要和api的基类名称一致
        if name == 'ApiClient':
            return type.__new__(mcs, name, bases, attrs)
        mappings = dict()
        for k, v in attrs.items():
            if issubclass(type(v), MethodClient):
                mappings[k] = v
        attrs['apis'] = mappings
        # for k in mappings.keys():
        #     attrs.pop(k)
        return type.__new__(mcs, name, bases, attrs)


class ApiClient(object, metaclass=ApiClientMeta):
    def __init__(self, host, port, url_prefix='/', use_ssl=False):
        self.host = host
        self.port = port
        self.url_prefix = url_prefix
        self.use_ssl = use_ssl
        self.init_host_port()

    def init_host_port(self):
        for k, v in self.apis.items():
            v.init_host_port(self.host, self.port, self.url_prefix, use_ssl=self.use_ssl)


#  ####### 以下为测试代码$##########3
class HelloClient(ApiClient):
    hello = GetClient('hello')
    post = PostClient('post')


if __name__ == '__main__':
    hello_client = HelloClient(host='127.0.0.1', port=15000, url_prefix='api')
    res = hello_client.hello(params={'name': 'chaos'})
    print(res)
