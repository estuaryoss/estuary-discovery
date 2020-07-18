import json
import logging
import threading

import requests

from rest.api.apiresponsehelpers.constants import Constants
from rest.api.apiresponsehelpers.error_codes import ErrorCodes
from rest.api.apiresponsehelpers.http_response import HttpResponse

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


class ThreadUtils:
    def __init__(self, apps, headers=dict()):
        self.apps = apps
        self.headers = headers
        self.response_list = []

    def get_threads_response(self):
        return self.response_list

    def get_url(self, app):
        return app.get('homePageUrl')

    def get_test_info(self, app):
        request_object = {
            "uri": "test",
            "method": 'GET',
            "headers": self.headers,  # forward headers if set like X-Request-ID or Token
            "data": None
        }

        try:
            response = self.send_http_request(app, request_object=request_object)
            test_info = response.json().get('description')
            test_info["homePageUrl"] = app.get('homePageUrl')
            test_info["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
            self.response_list.append(test_info)
        except:
            self.response_list.append({"err": f"{request_object}"})

    def spawn_threads_get_test_info(self):
        threads = [threading.Thread(target=self.get_test_info, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()

    def get_request_get_deployment_info(self, app):
        request_object = {
            "uri": "docker/deployments",
            "method": 'GET',
            "headers": self.headers,
            "data": None
        }

        try:
            response = self.send_http_request(app, request_object=request_object)
            deployment_info = response.json().get('message')
            for deployment in deployment_info:
                deployment["homePageUrl"] = app.get('homePageUrl')
                deployment["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                self.response_list.append(deployment)
        except:
            self.response_list.append({"err": f"{request_object}"})

    def spawn_threads_get_deployment_info(self):
        threads = [threading.Thread(target=self.get_request_get_deployment_info, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()

    def send_http_request(self, app, request_object):
        http = HttpResponse()
        try:
            response = requests.request(url=f'{self.get_url(app)}{request_object.get("uri")}',
                                        method=request_object.get('method'), data=request_object.get('data'),
                                        headers=request_object.get("headers"), timeout=5)
        except Exception as e:
            exception = "Exception({})".format(e.__str__())
            response = requests.Response(
                json.dumps(http.response(Constants.TARGET_UNREACHABLE, ErrorCodes.HTTP_CODE.get(
                    Constants.TARGET_UNREACHABLE) % f'{self.get_url(app)}{request_object.get("uri")}', exception)),
                404,
                mimetype="application/json")

        return response

    def send_testrunner_request(self, app, request_object):
        try:
            response = self.send_http_request(app, request_object=request_object).json()
        except:
            response = self.send_http_request(app, request_object=request_object).text

        self.response_list.append(response)

    def spawn_threads_send_testrunner_request(self, request_object):
        threads = [threading.Thread(target=self.send_testrunner_request, args=(app, request_object,)) for app in
                   self.apps]
        for thread in threads:
            thread.start()
            thread.join()
