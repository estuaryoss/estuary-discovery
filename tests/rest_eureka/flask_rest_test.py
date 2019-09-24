#!/usr/bin/env python3
import os
import time
import unittest

import requests
from py_eureka_client import eureka_client


class EstuaryStackApps:

    @staticmethod
    def get_supported_apps():
        return ["estuary-testrunner", "estuary-deployer", "estuary-discovery"]


class Constants:
    DOCKER_PATH = "/tmp/"

    SUCCESS = "1000"
    JINJA2_RENDER_FAILURE = "1001"
    GET_EUREKA_APPS_FAILED = "1002"
    GET_CONTAINER_ENV_VAR_FAILURE = "1003"


class ErrorCodes:
    HTTP_CODE = {
        Constants.SUCCESS: "success",
        Constants.JINJA2_RENDER_FAILURE: "jinja2 render failed",
        Constants.GET_EUREKA_APPS_FAILED: "Failed to get apps from Eureka discovery_ip '%s'",
        Constants.GET_CONTAINER_ENV_VAR_FAILURE: "Failed to get env var '%s'"
    }


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
    expected_version = "2.0.2"
    discovery_ip = "estuary-discovery"
    testrunner_ip = "estuary-testrunner"
    deployer_ip = "estuary-deployer"
    server_port = "8080"  # all have 8080

    def test_eureka_registration(self):
        up_services = EurekaClient(f"{os.environ.get('EUREKA_SERVER')}").get_apps()
        self.assertEqual(len(up_services), 3)

    def test_geteureka_apps(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 3)
        self.assertEqual(len(body.get('message').get(self.discovery_ip)), 1)
        self.assertEqual(len(body.get('message').get(self.testrunner_ip)), 1)
        self.assertEqual(len(body.get('message').get(self.deployer_ip)), 1)
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("homePageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/")
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("statusPageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message').get(self.discovery_ip)[0].get("healthCheckUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message').get(self.testrunner_ip)[0].get("ipAddr"), self.testrunner_ip)
        self.assertEqual(body.get('message').get(self.testrunner_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('message').get(self.deployer_ip)[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('message').get(self.deployer_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_geteureka_apps_testrunner(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps/estuary-testrunner")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 1)
        self.assertEqual(len(body.get('message')[0]), 6)
        self.assertEqual(body.get('message')[0].get("ipAddr"), self.testrunner_ip)
        self.assertEqual(body.get('message')[0].get("app"), self.testrunner_ip)
        self.assertEqual(body.get('message')[0].get("homePageUrl"), f"http://{self.testrunner_ip}:{self.server_port}/")
        self.assertEqual(body.get('message')[0].get("healthCheckUrl"),
                         f"http://{self.testrunner_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message')[0].get("statusPageUrl"),
                         f"http://{self.testrunner_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message')[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_geteureka_apps_deployer(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps/estuary-deployer")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 1)
        self.assertEqual(len(body.get('message')[0]), 6)
        self.assertEqual(body.get('message')[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('message')[0].get("port"), self.server_port)
        self.assertEqual(body.get('message')[0].get("app"), self.deployer_ip)
        self.assertEqual(body.get('message')[0].get("homePageUrl"), f"http://{self.deployer_ip}:{self.server_port}/")
        self.assertEqual(body.get('message')[0].get("healthCheckUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message')[0].get("statusPageUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_geteureka_apps_discovery(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps/estuary-discovery")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 1)
        self.assertEqual(len(body.get('message')[0]), 6)
        self.assertEqual(body.get('message')[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('message')[0].get("port"), self.server_port)
        self.assertEqual(body.get('message')[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('message')[0].get("homePageUrl"), f"http://{self.discovery_ip}:{self.server_port}/")
        self.assertEqual(body.get('message')[0].get("healthCheckUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('message')[0].get("statusPageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_geteureka_apps_empty_list(self):
        app = "whatever"
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps/{app}")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('message')), 0)
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_gettests(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/gettests")
        body = response.json()
        expected_port = 8080
        expected_ip = "estuary-testrunner"
        # print(dump.dump_all(response))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 1)
        self.assertEqual(body.get('message')[0].get("started"), "true")
        self.assertEqual(body.get('message')[0].get("ip_port"), f"{expected_ip}:{expected_port}")
        self.assertEqual(body.get('message')[0].get("homePageUrl"), f"http://{expected_ip}:{expected_port}/gettestinfo")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_getdeployments(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/getdeployments")
        expected_port = 8080
        expected_ip = "estuary-deployer"

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('message')), 2)
        self.assertEqual(len(body.get('message')[0].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('message')[0].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('message')[0].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/getdeploymentinfo")
        self.assertEqual(len(body.get('message')[1].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('message')[1].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('message')[1].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/getdeploymentinfo")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('time'))

    def test_time_of_100_requests(self):
        repetitions = 100
        start = time.time()
        for i in range(1, repetitions):
            response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/geteurekaapps")
            self.assertEqual(response.status_code, 200)
        end = time.time()
        print(f"made {repetitions} geteurekaapps repetitions in {end - start} s")


if __name__ == '__main__':
    unittest.main()
