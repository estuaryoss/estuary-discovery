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
        return ["estuary-agent", "estuary-deployer", "estuary-discovery"]


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
    agent_ip = "estuary-agent"
    deployer_ip = "estuary-deployer"
    server_port_ext = "8081"
    server_port = "8080"  # all have 8080
    no_of_deployers = 1
    no_of_agents = 1
    no_of_discovery = 1

    def test_eureka_registration(self):
        up_services = EurekaClient("http://localhost:8080/eureka/v2").get_apps()
        self.assertEqual(len(up_services), 3)

    def test_geteureka_apps(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps", headers=headers)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')),
                         3)  # its 3 because we have only 3 keys: deployer, agent, discovery
        self.assertEqual(len(body.get('description').get(self.discovery_ip)), self.no_of_discovery)
        self.assertEqual(len(body.get('description').get(self.agent_ip)), self.no_of_agents)
        self.assertEqual(len(body.get('description').get(self.deployer_ip)), self.no_of_deployers)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("homePageUrl"),
                         f"{self.home_url_int}:{self.server_port}/")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("statusPageUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("healthCheckUrl"),
                         f"{self.home_url_int}:{self.server_port}/ping")
        self.assertIn(self.agent_ip, body.get('description').get(self.agent_ip)[0].get("ipAddr"))
        self.assertEqual(body.get('description').get(self.agent_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('description').get(self.deployer_ip)[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('description').get(self.deployer_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_agent(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/estuary-agent", headers=headers)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_agents)
        self.assertEqual(len(body.get('description')[0]), 7)
        # self.assertEqual(body.get('description')[0].get("ipAddr"), self.agent_ip)
        # self.assertEqual(body.get('description')[0].get("app"), self.agent_ip)
        # self.assertEqual(body.get('description')[0].get("homePageUrl"), f"http://{self.agent_ip}:{self.server_port}/")
        # self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
        #                  f"http://{self.agent_ip}:{self.server_port}/ping")
        # self.assertEqual(body.get('description')[0].get("statusPageUrl"),
        #                  f"http://{self.agent_ip}:{self.server_port}/ping")
        # self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_deployer(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/estuary-deployer", headers=headers)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_deployers)
        self.assertEqual(len(body.get('description')[0]), 7)
        self.assertEqual(body.get('description')[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('description')[0].get("app"), self.deployer_ip)
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/docker/")
        self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/docker/ping")
        self.assertEqual(body.get('description')[0].get("statusPageUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/docker/about")
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_discovery(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/estuary-discovery", headers=headers)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_discovery)
        self.assertEqual(len(body.get('description')[0]), 7)
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

    def test_geteureka_apps_empty_list(self):
        app = "whatever"
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/{app}", headers=headers)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 0)
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_gettests(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/commandsdetached", headers=headers)
        body = response.json()
        expected_ip = "estuary-agent"
        print(f"! Active test sessions response : {dump.dump_all(response)}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 1)  # 1 test active
        self.assertIn(f"{expected_ip}", body.get('description')[0].get("ip_port"))
        self.assertIn(f"http://{expected_ip}", body.get('description')[0].get("homePageUrl"))
        self.assertIsInstance(body.get('description')[0].get("started"), bool)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_gettests_unauthorized(self):
        headers = {'Token': 'whateverinvalid'}
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/commandsdetached", headers=headers)
        headers = response.headers

        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_getdeployments(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/deployments", headers=headers)
        expected_port = 8080
        expected_ip = "estuary-deployer"
        print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 2)
        self.assertEqual(len(body.get('description')[0].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[0].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/docker/")
        self.assertEqual(len(body.get('description')[1].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[1].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[1].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/docker/")
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_getdeployments_unauthorized(self):
        xid = 'whatever'
        headers = {
            'Token': 'whateverinvalid',
            'X-Request-ID': xid
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/deployments", headers=headers)

        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertEqual(headers.get('X-Request-ID'), xid)

    def test_time_of_10_requests(self):
        repetitions = 10
        start = time.time()
        headers = {
            'Token': 'None'
        }
        for _ in range(1, repetitions):
            response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps", headers=headers)
            self.assertEqual(response.status_code, 200)
        end = time.time()
        print(f"made {repetitions} get eureka apps repetitions in {end - start} s")

    def test_get_agents_file_missing_file_path_n(self):
        header_key = 'File-Path'
        headers = {
            'whatever': '100',
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(ErrorMessage.HTTP_CODE.get(ApiCode.HTTP_HEADER_NOT_PROVIDED.value) % header_key,
                      body.get('description')[0].get('description'))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_agents_file_p(self):
        headers = {
            'File-Path': '/etc/hostname',
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertGreater(len(body.get('description')[0]), 8)

    def test_get_agents_file_file_not_found(self):
        expected = "no such file"
        headers = {
            'File-Path': '/dummy_path',
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertIn(expected, body.get('description')[0].get('description'))

    def test_agent_teststart_broadcast_p(self):
        cmds = "ls -lrt\n"
        test_id = "100"
        headers = {
            'Token': 'None'
        }
        response = requests.post(f"{self.home_url}:{self.server_port_ext}/agents/commanddetached/{test_id}",
                                 data=cmds, headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertEqual(body.get('description')[0].get('description'), test_id)
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/commanddetached", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertEqual(body.get('description')[0].get('description').get('id'), test_id)

    def test_deployer_ping_broadcast_p(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/deployers/about", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)
        self.assertIn("system", body.get('description')[0].get('description'))

    def test_agent_teststart_unicast_p(self):
        test_id = ["1", "2"]
        cmds = ["echo {}".format(test_id[0]), "echo {}".format(test_id[1])]

        # get eureka apps agent
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/agent", headers=headers)
        # print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast teststart request and check the results
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr'), item.get('port')),
                'Token': 'None'
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(
                f"{self.home_url}:{self.server_port_ext}/agents/commanddetached/{test_id[i]}",
                data=cmds[i], headers=headers)
            body = response.json()
            print(dump.dump_response(response))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertEqual(body.get('description')[0].get('description'), test_id[i])

            headers = {
                'Token': 'None'
            }
            response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/commanddetached", headers=headers)
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertIn(test_id[i], [body.get('description')[0].get('description').get('id')])

    def test_deployer_unicast_p(self):
        # get eureka apps agent
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/deployer", headers=headers)
        # print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast request and check the results
        deployer_apps = body.get('description')
        for i, item in enumerate(deployer_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr'), item.get('port')),
                'Token': 'None'
            }

            # send unicast message to the deployers with the ip:port
            response = requests.get(
                f"{self.home_url}:{self.server_port_ext}/deployers/about", headers=headers)
            body = response.json()
            print(dump.dump_response(response))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertIn("system", body.get('description')[0].get('description'))

    def test_agent_teststart_unicast_wrong_ipport_p(self):
        test_id = ["1", "2"]
        cmds = ["echo {}".format(test_id[0]), "echo {}".format(test_id[1])]

        # get eureka apps agent
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"{self.home_url}:{self.server_port_ext}/eurekaapps/agent", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 1)

        # send unicast teststart request and check the results
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr') + "dummy", item.get('port')),
                'Token': 'None'
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(
                f"{self.home_url}:{self.server_port_ext}/agents/commanddetached/{test_id[i]}",
                data=cmds[i], headers=headers)
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 0)
            headers = {
                'Token': 'None'
            }
            response = requests.get(f"{self.home_url}:{self.server_port_ext}/agents/commanddetached", headers=headers)
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)


if __name__ == '__main__':
    unittest.main()
