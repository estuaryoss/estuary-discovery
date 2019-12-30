import logging
import threading

import requests

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


class ThreadUtils:
    def __init__(self, apps):
        self.apps = apps
        self.response_list = []

    def get_threads_response(self):
        return self.response_list

    def get_url(self, app):
        return app.get('homePageUrl')

    def get_test_info(self, app):
        request_object = {
            "uri": "gettestinfo",
            "method": 'GET',
            "headers": {"Content-Type": "application/json"},
            "data": ""
        }

        try:
            response = self.send_http_request(app, request_object=request_object)
            test_info = response.json().get('message')
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
            "uri": "getdeploymentinfo",
            "method": 'GET',
            "headers": {"Content-Type": "application/json"},
            "data": ""
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
        if request_object.get('method') == 'GET':
            response = requests.get(f'{self.get_url(app)}{request_object.get("uri")}',
                                    headers=request_object.get("headers"), timeout=3)
        elif request_object.get('method') == 'POST':
            response = requests.post(f'{self.get_url(app)}{request_object.get("uri")}',
                                     data=request_object.get('data'),
                                     headers=request_object.get("headers"), timeout=3)
        else:
            pass

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
