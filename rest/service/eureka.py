import re

import py_eureka_client.eureka_client as eureka_client


class Eureka:
    def __init__(self, host):
        self.host = host

    def get_eureka_apps(self):
        apps_list = {}
        for app in eureka_client.get_applications(eureka_server=self.host).applications:
            for instance in app.up_instances:
                app_name = str(instance.app.lower())
                if app_name not in apps_list:
                    apps_list[app_name] = []
                apps_list[app_name].append({
                    "ipAddr": str(instance.ipAddr),
                    "port": str(instance.port.port),
                    "securePort": str(instance.securePort.port),
                    "app": app_name,
                    "metadata": instance.metadata,
                    "homePageUrl": str(instance.homePageUrl),
                    "healthCheckUrl": str(instance.healthCheckUrl),
                    "statusPageUrl": str(instance.statusPageUrl)
                })
        return apps_list

    def get_type_eureka_apps(self, application=None):
        apps_list = []
        all_apps_list = self.get_eureka_apps()
        for key in all_apps_list:
            [apps_list.append(app) for app in all_apps_list[key] if re.search(rf'{application}', key)]

        return apps_list

    def get_eureka_host(self):
        return self.host
