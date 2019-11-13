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
        return f"{app.get('homePageUrl')}"

    def get_request_testrunners(self, app):
        try:
            response = requests.get(f"{self.get_url(app)}gettestinfo", timeout=3)
            test_info = response.json().get('message')
            test_info["homePageUrl"] = f"{app.get('homePageUrl')}"
            test_info["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
            self.response_list.append(test_info)
        except:
            pass

    def get_request_deployers(self, app):
        try:
            response = requests.get(f"{self.get_url(app)}getdeploymentinfo", timeout=3)
            deployment_info = response.json().get('message')
            for deployment in deployment_info:
                deployment["homePageUrl"] = f"{app.get('homePageUrl')}"
                deployment["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                self.response_list.append(deployment)
        except:
            pass

    def get_results_testrunners(self, app, headers):
        try:
            response = requests.get(f"{app.get('homePageUrl')}getfile", headers=headers, timeout=3)
            app['fileContent'] = response.text
            self.response_list.append(app)
        except:
            pass

    def spawn_threads_testrunners(self):
        threads = [threading.Thread(target=self.get_request_testrunners, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()

    def spawn_threads_deployers(self):
        threads = [threading.Thread(target=self.get_request_deployers, args=(app,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()

    def spawn_threads_get_files(self, headers):
        threads = [threading.Thread(target=self.get_results_testrunners, args=(app, headers,)) for app in self.apps]
        for thread in threads:
            thread.start()
            thread.join()
