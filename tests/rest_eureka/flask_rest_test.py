#!/usr/bin/env python3
import time
import unittest

import requests
from py_eureka_client import eureka_client
from requests_toolbelt.utils import dump

from rest.api.constants.api_constants import ApiCode
from rest.api.responsehelpers.error_codes import ErrorMessage


class EstuaryStackApps:

    @staticmethod
    def get_supported_apps():
        return ["estuary-agent", "estuary-discovery"]


class EurekaClient:

    def __init__(self, host):
        self.host = host

    def get_apps(self):
        apps_list = []
        print("Getting apps from eureka server {} ... \n".format(self.host))
        for app in eureka_client.get_applications(eureka_server=self.host).applications:
            for instance in app.up_instances:
                # print(instance.app)
                apps_list.append(instance.hostName)
        return apps_list


class FlaskServerEurekaTestCase(unittest.TestCase):
    discovery_ip = "estuary-discovery"
    home_url_int = f"http://{discovery_ip}"
    home_url = "http://localhost"
    agent_ip = "estuary-agent-java"
    server_port_ext = "8081"
    server_port = "8080"  # all have 8080
    no_of_agents = 1
    no_of_discovery = 1
    username = "admin"
    password = "estuaryoss123!"

    def test_eureka_registration(self):
        up_services = EurekaClient("http://localhost:8080/eureka/v2").get_apps()
        self.assertEqual(len(up_services), 2)

    def test_get_eureka_apps(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps", headers=headers,
                                auth=(self.username, self.password))

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 2)
        self.assertEqual(len(body.get('description').get(self.discovery_ip)), self.no_of_discovery)
        self.assertEqual(len(body.get('description').get(self.agent_ip)), self.no_of_agents)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("homePageUrl"),
                         f"{self.home_url_int}:{self.server_port}/")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("statusPageUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("healthCheckUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertEqual(body.get('description').get(self.agent_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_eureka_apps_agent(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/estuary-agent", headers=headers,
                                auth=(self.username, self.password))

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_agents)
        self.assertGreaterEqual(len(body.get('description')[0]), 8)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_eureka_apps_discovery(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/discovery", headers=headers,
                                auth=(self.username, self.password))

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_discovery)
        self.assertGreaterEqual(len(body.get('description')[0]), 8)
        self.assertEqual(body.get('description')[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('description')[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"{self.home_url_int}:{self.server_port}/")
        self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertEqual(body.get('description')[0].get("statusPageUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_eureka_apps_empty_list(self):
        app = "whatever"
        headers = {}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/{app}", headers=headers,
                                auth=(self.username, self.password))

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 0)
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_finished_commands(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/commands/finished", headers=headers,
                                auth=(self.username, self.password))
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 1)
        self.assertIsNotNone(body.get('description')[0].get("ip_port"))
        self.assertIsNotNone(body.get('description')[0].get("homePageUrl"))
        self.assertIsInstance(body.get('description')[0].get('description'), list)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_commands_unauthorized(self):
        headers = {}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/commands", headers=headers,
                                auth=(self.username, "invalidPasswd"))
        headers = response.headers

        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_time_of_x_requests(self):
        repetitions = 5
        start = time.time()
        headers = {}
        for _ in range(1, repetitions):
            response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps", headers=headers,
                                    auth=(self.username, self.password))
            self.assertEqual(response.status_code, 200)
        end = time.time()
        print(f"made {repetitions} get eureka apps repetitions in {end - start} s")

    def test_get_agents_file_missing_file_path_n(self):
        headers = {
            "Content-Type": "application/json",
            'whatever': '100'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers,
                                auth=(self.username, self.password))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Exception",
                      body.get('description')[0].get('description'))
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_agents_file_p(self):
        headers = {
            'File-Path': '/etc/hostname'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers,
                                auth=(self.username, self.password))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertGreater(len(body.get('description')[0]), 8)

    def test_get_agents_file_file_not_found(self):
        expected = "Exception"
        headers = {
            'File-Path': '/dummy_path'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers,
                                auth=(self.username, self.password))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertIn(expected, body.get('description')[0].get('description'))

    def test_agent_command_start_broadcast_p(self):
        cmd = "echo 1"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(f"{self.home_url}:{self.server_port_ext}/agents/commands",
                                 data=cmd, headers=headers, auth=(self.username, self.password))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(body.get('description'), list)
        self.assertIsInstance(body.get('description')[0].get('description').get('commands').get(cmd), dict)

    def test_agent_command_unicast_p(self):
        cmd = "echo 1"

        # get eureka apps agent
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/agent", headers=headers,
                                auth=(self.username, self.password))
        # print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast command
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr'), item.get('port')),
                "Content-Type": "application/json"
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(
                f"{self.home_url}:{self.server_port_ext}/agents/commands", data=cmd, headers=headers,
                auth=(self.username, self.password))
            body = response.json()
            print(dump.dump_response(response))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertIsInstance(body.get('description')[0].get('description').get('commands').get(cmd), dict)

    def test_agent_command_start_unicast_by_home_page_url(self):
        cmd = "echo 1"

        # get eureka apps agent
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/agent", headers=headers,
                                auth=(self.username, self.password))
        # print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast teststart request and check the results
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'HomePageUrl': item.get('homePageUrl'),
                "Content-Type": "application/json"
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(
                f"{self.home_url}:{self.server_port_ext}/agents/commands",
                data=cmd, headers=headers, auth=(self.username, self.password))
            body = response.json()
            print(dump.dump_response(response))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertIsInstance(body.get('description')[0].get('description').get('commands').get(cmd), dict)

    def test_agent_command_start_unicast_wrong_ip_port(self):
        cmd = "echo 1"

        # get eureka apps agent
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eureka/apps/agent", headers=headers,
                                auth=(self.username, self.password))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast command
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr') + "invalidThing", item.get('port')),
                "Content-Type": "application/json"
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(
                f"{self.home_url}:{self.server_port_ext}/agents/commands",
                data=cmd, headers=headers, auth=(self.username, self.password))
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 0)


if __name__ == '__main__':
    unittest.main()
