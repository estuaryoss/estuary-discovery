from py_eureka_client import eureka_client


class EurekaUtils:

    @staticmethod
    def get_eureka_apps(host):
        apps_list = {}
        for app in eureka_client.get_applications(eureka_server=f"{host}").applications:
            for instance in app.up_instances:
                # [ip, app, port] = instance.instanceId.split(":")
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

    @staticmethod
    def get_type_eureka_apps(host, type=None):
        apps_list = []
        all_apps_list = EurekaUtils.get_eureka_apps(host)
        for key in all_apps_list:
            if type in key:
                for item in all_apps_list[key]:
                    apps_list.append(item)

        return apps_list
