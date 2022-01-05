import logging
import pathlib
import re
import threading
from secrets import token_hex

import requests

from rest.api.constants.api_constants import ApiCode
from rest.api.responsehelpers.error_codes import ErrorMessage
from rest.api.responsehelpers.http_response import HttpResponse
from rest.utils.io_utils import IOUtils

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')


class ThreadUtils:
    download_folder = f"{pathlib.Path(__file__).parent.resolve()}/downloads"

    def __init__(self, apps, headers):
        self.apps = apps
        self.headers = headers
        self.response_list = []
        self.__is_response_zip = False
        self.__source_zip_folder = token_hex(8)

    def get_threads_response(self):
        return self.response_list

    def is_response_zip(self):
        return self.__is_response_zip

    def get_source_zip_folder(self):
        return self.__source_zip_folder

    @staticmethod
    def get_url(app):
        return app.get('homePageUrl')

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
                                        timeout=10,
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
            response["homePageUrl"] = app.get('homePageUrl')
            response["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"

            self.response_list.append(response)
        except:
            file_name = re.findall(".*filename=(.+)", resp.headers["Content-Disposition"])[0] if resp.headers.get(
                "Content-Disposition") else ""

            self.__is_response_zip = True
            IOUtils.create_dir(f"{self.download_folder}/{self.__source_zip_folder}")
            IOUtils.write_to_file(
                f"{self.download_folder}/{self.__source_zip_folder}/{app.get('ipAddr')}_{app.get('port')}_{file_name}",
                resp.content)

    def spawn_threads_send_request(self, request_object):
        threads = [threading.Thread(target=self.send_request, args=(app, request_object,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()
