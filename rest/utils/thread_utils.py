import logging
import threading

import requests
from requests_toolbelt.utils import dump

from rest.api.constants.api_constants import ApiCode
from rest.api.responsehelpers.error_codes import ErrorMessage
from rest.api.responsehelpers.http_response import HttpResponse

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')


class ThreadUtils:
    def __init__(self, apps, headers):
        self.apps = apps
        self.headers = headers
        self.response_list = []

    def get_threads_response(self):
        return self.response_list

    @staticmethod
    def get_url(app):
        return app.get('homePageUrl')

    def get_command_detached_info(self, app):
        request_object = {
            "uri": "commanddetached",
            "method": "GET",
            "headers": self.headers,  # forward headers if set like X-Request-ID or Token
            "data": None
        }

        response = self.send_http_request(app, request_object=request_object)

        if response.status_code == 200:
            try:
                test_info = response.json().get('description')
                test_info["homePageUrl"] = app.get('homePageUrl')
                test_info["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                self.response_list.append(test_info)
            except:
                self.response_list.append(str(dump.dump_all(response)))
        else:
            self.response_list.append(str(dump.dump_all(response)))

    def spawn_threads_get_test_info(self):
        threads = [threading.Thread(target=self.get_command_detached_info, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def get_request_get_deployment_info(self, app):
        request_object = {
            "uri": "docker/deployments",
            "method": "GET",
            "headers": self.headers,
            "data": None
        }

        response = self.send_http_request(app, request_object=request_object)

        if response.status_code == 200:
            try:
                deployment_info = response.json().get('description')
                for deployment in deployment_info:
                    deployment["homePageUrl"] = app.get('homePageUrl')
                    deployment["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                    self.response_list.append(deployment)
            except:
                self.response_list.append(str(dump.dump_all(response)))
        else:
            self.response_list.append(str(dump.dump_all(response)))

    def spawn_threads_get_deployment_info(self):
        threads = [threading.Thread(target=self.get_request_get_deployment_info, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def send_http_request(self, app, request_object):
        logging.debug({"url": f'{self.get_url(app)}{request_object.get("uri")}',
                       "method": request_object.get('method'),
                       "headers": request_object.get("headers"),
                       "data": request_object.get("data")})

        try:
            response = requests.request(method=request_object.get('method'),
                                        url=f'{self.get_url(app)}{request_object.get("uri")}',
                                        headers=request_object.get("headers"),
                                        data=request_object.get('data'),
                                        timeout=3)
        except Exception as e:
            response = HttpResponse.response(
                ApiCode.TARGET_UNREACHABLE.value,
                ErrorMessage.HTTP_CODE.get(
                    ApiCode.TARGET_UNREACHABLE.value) % f'{self.get_url(app)}{request_object.get("uri")}',
                "Exception({})".format(e.__str__()))

        return response

    def send_request(self, app, request_object):
        resp = self.send_http_request(app, request_object=request_object)

        try:
            response = resp.json()
        except:
            try:
                response = resp.text
            except:
                response = resp

        self.response_list.append(response)

    def spawn_threads_send_request(self, request_object):
        threads = [threading.Thread(target=self.send_request, args=(app, request_object,)) for app in
                   self.apps]
        for thread in threads:
            thread.start()
            thread.join()
