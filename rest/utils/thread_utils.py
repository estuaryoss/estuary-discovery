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

    def __get_commands_info(self, app, uri):
        request_object = {
            "uri": uri,
            "method": "GET",
            "headers": self.headers,  # forward headers if set like X-Request-ID or Authorization
            "data": None
        }

        response = self.send_http_request(app, request_object=request_object)

        if response.status_code == 200:
            try:
                commands_info = response.json()
                commands_info["homePageUrl"] = app.get('homePageUrl')
                commands_info["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                self.response_list.append(commands_info)
            except:
                self.response_list.append(str(dump.dump_all(response)))
        else:
            self.response_list.append(str(dump.dump_all(response)))

    def spawn_threads_get_active_commands_info(self):
        threads = [threading.Thread(target=self.__get_commands_info, args=(app, "commands",)) for app in self.apps]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def spawn_threads_get_finished_commands_info(self):
        threads = [threading.Thread(target=self.__get_commands_info, args=(app, "commandsfinished",)) for app in
                   self.apps]
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
                                        timeout=3,
                                        verify=False)
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
