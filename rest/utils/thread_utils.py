import logging
import threading

from rest.utils.rest_utils import RestUtils

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


class ThreadUtils:
    def __init__(self, apps):
        self.apps = apps
        self.response_list = []

    def get_url(self, app):
        return f"{app.get('homePageUrl')}"

    def get_request_testrunners(self, app):
        try:
            response = RestUtils().get(f"{self.get_url(app)}gettestinfo")
            testinfo = response.json().get('message')
            testinfo["homePageUrl"] = f"{app.get('homePageUrl')}gettestinfo"
            testinfo["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
            self.response_list.append(testinfo)
        except:
            pass

    def get_request_deployers(self, app):
        try:
            response = RestUtils().get(f"{self.get_url(app)}getdeploymentinfo")
            deploymentinfo = response.json().get('message')
            for deployment in deploymentinfo:
                deployment["homePageUrl"] = f"{app.get('homePageUrl')}getdeploymentinfo"
                deployment["ip_port"] = f"{app.get('ipAddr')}:{app.get('port')}"
                self.response_list.append(deployment)
        except:
            pass

    def get_list(self):
        return self.response_list

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
