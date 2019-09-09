#!/usr/bin/env python3
import os
import unittest

import requests
from py_eureka_client import eureka_client

from tests.rest_eureka.constants import Constants
from tests.rest_eureka.error_codes import ErrorCodes


class EurekaClient:

    def __init__(self, host):
        self.host = host

    def get_apps(self):
        apps_list = []
        print(f"Getting apps from eureka server {self.host} ... \n")
        for app in eureka_client.get_applications(eureka_server=f"{self.host}").applications:
            for instance in app.up_instances:
                # print(instance.app)
                apps_list.append(instance.hostName)
        return apps_list


class FlaskServerEurekaTestCase(unittest.TestCase):
    expected_version = "1.0.0"
    server_ip = "estuary-discovery"
    server_port = "8080"

    def test_eureka_registration(self):
        up_services = EurekaClient(f"{os.environ.get('EUREKA_SERVER')}").get_apps()
        self.assertEqual(len(up_services), 1)  # 1 instance registered
        self.assertEqual(up_services[0], self.server_ip)  # 1 instance registered

    def test_geteureka_apps(self):
        response = requests.get(self.server_ip + f"/geteurekaapps")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 1)
        self.assertEqual(len(body.get('message').get(self.server_ip)), 1)
        self.assertEqual(len(body.get('message').get(self.server_ip).get("ip")), self.server_ip)
        self.assertEqual(len(body.get('message').get(self.server_ip).get("port")), self.server_port)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))


if __name__ == '__main__':
    unittest.main()
