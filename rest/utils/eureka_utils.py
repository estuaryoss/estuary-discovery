import re

import py_eureka_client.eureka_client as eureka_client


class EurekaUtils:
    def __init__(self, host):
        self.host = host

    def get_eureka_apps(self):
        apps_list = {}
        for app in eureka_client.get_applications(eureka_server=self.host).applications:
            for instance in app.up_instances:
                app = str(instance.app.lower())
                if app not in apps_list:
                    apps_list[app] = []
                apps_list[app].append({
                    "ipAddr": str(instance.ipAddr),
                    "port": str(instance.port.port),
                    "app": app,
                    "homePageUrl": str(instance.homePageUrl),
                    "healthCheckUrl": str(instance.healthCheckUrl),
                    "statusPageUrl": str(instance.statusPageUrl)
                })
        return apps_list

    def get_type_eureka_apps(self, application=None):
        apps_list = []
        all_apps_list = self.get_eureka_apps()
        for key in all_apps_list:
            pattern = rf'{application}'
            match = re.search(pattern, key)
            if match:
                for item in all_apps_list[key]:
                    apps_list.append(item)

        return apps_list

    def get_eureka_host(self):
        return self.host
