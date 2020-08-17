#!/usr/bin/env python3
import os
import time
import unittest

import requests
from py_eureka_client import eureka_client
from requests_toolbelt.utils import dump


class EstuaryStackApps:

    @staticmethod
    def get_supported_apps():
        return ["estuary-agent", "estuary-deployer", "estuary-discovery"]


class Constants:
    DOCKER_PATH = "/tmp/"

    SUCCESS = 1000
    JINJA2_RENDER_FAILURE = 1001
    GET_EUREKA_APPS_FAILED = 1002
    GET_CONTAINER_ENV_VAR_FAILURE = 1003
    GET_TESTS_FAILED = 1004
    GET_DEPLOYMENTS_FAILED = 1005
    GET_TEST_RESULTS_FAILED = 1006
    HTTP_HEADER_NOT_PROVIDED = 1007


class ErrorCodes:
    HTTP_CODE = {
        Constants.SUCCESS: "Success",
        Constants.JINJA2_RENDER_FAILURE: "jinja2 render failed",
        Constants.GET_EUREKA_APPS_FAILED: "Failed to get apps from Eureka server '%s'",
        Constants.GET_CONTAINER_ENV_VAR_FAILURE: "Failed to get env var '%s'",
        Constants.GET_TESTS_FAILED: "Failed to get tests list",
        Constants.GET_DEPLOYMENTS_FAILED: "Failed to get deployments list",
        Constants.GET_TEST_RESULTS_FAILED: "Failed to get test results list",
        Constants.HTTP_HEADER_NOT_PROVIDED: "Http header value not provided: '%s'",
    }


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
    expected_version = "4.0.1"
    discovery_ip = "estuary-discovery"
    # discovery_ip = "localhost"
    agent_ip = "estuary-agent"
    deployer_ip = "estuary-deployer"
    server_port = "8080"  # all have 8080
    no_of_deployers = 1
    no_of_agents = 2
    no_of_discovery = 1

    def test_eureka_registration(self):
        up_services = EurekaClient(f"{os.environ.get('EUREKA_SERVER')}").get_apps()
        self.assertEqual(len(up_services), 4)

    def test_geteureka_apps(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')),
                         3)  # its 3 because we have only 3 keys: deployer, agent, discovery
        self.assertEqual(len(body.get('description').get(self.discovery_ip)), 1)
        self.assertEqual(len(body.get('description').get(self.agent_ip)), 2)
        self.assertEqual(len(body.get('description').get(self.deployer_ip)), 1)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("homePageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("statusPageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('description').get(self.discovery_ip)[0].get("healthCheckUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertIn(self.agent_ip, body.get('description').get(self.agent_ip)[0].get("ipAddr"))
        self.assertEqual(body.get('description').get(self.agent_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('description').get(self.deployer_ip)[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('description').get(self.deployer_ip)[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_agent(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/estuary-agent")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_agents)
        self.assertEqual(len(body.get('description')[0]), 6)
        # self.assertEqual(body.get('description')[0].get("ipAddr"), self.agent_ip)
        # self.assertEqual(body.get('description')[0].get("app"), self.agent_ip)
        # self.assertEqual(body.get('description')[0].get("homePageUrl"), f"http://{self.agent_ip}:{self.server_port}/")
        # self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
        #                  f"http://{self.agent_ip}:{self.server_port}/ping")
        # self.assertEqual(body.get('description')[0].get("statusPageUrl"),
        #                  f"http://{self.agent_ip}:{self.server_port}/ping")
        # self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_deployer(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/estuary-deployer")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_deployers)
        self.assertEqual(len(body.get('description')[0]), 6)
        self.assertEqual(body.get('description')[0].get("ipAddr"), self.deployer_ip)
        self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('description')[0].get("app"), self.deployer_ip)
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/")
        self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/api/docs")
        self.assertEqual(body.get('description')[0].get("statusPageUrl"),
                         f"http://{self.deployer_ip}:{self.server_port}/api/docs")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_discovery(self):
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/estuary-discovery")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), self.no_of_discovery)
        self.assertEqual(len(body.get('description')[0]), 6)
        self.assertEqual(body.get('description')[0].get("ipAddr"), self.discovery_ip)
        self.assertEqual(body.get('description')[0].get("port"), self.server_port)
        self.assertEqual(body.get('description')[0].get("app"), self.discovery_ip)
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/")
        self.assertEqual(body.get('description')[0].get("healthCheckUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('description')[0].get("statusPageUrl"),
                         f"http://{self.discovery_ip}:{self.server_port}/ping")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_geteureka_apps_empty_list(self):
        app = "whatever"
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/{app}")

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 0)
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_gettests(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/commandsdetached", headers=headers)
        body = response.json()
        expected_ip = "estuary-agent"
        print(f"! Active test sessions response : {dump.dump_all(response)}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 2)  # 2 tests active
        self.assertIn(f"{expected_ip}", body.get('description')[0].get("ip_port"))
        self.assertIn(f"http://{expected_ip}", body.get('description')[0].get("homePageUrl"))
        self.assertIn(f"http://{expected_ip}", body.get('description')[1].get("homePageUrl"))
        self.assertIsInstance(body.get('description')[0].get("started"), bool)
        self.assertIsInstance(body.get('description')[1].get("started"), bool)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_gettests_unauthorized(self):
        headers = {'Token': 'whateverinvalid'}
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/commandsdetached", headers=headers)
        headers = response.headers

        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_getdeployments(self):
        headers = {
            'Token': 'None'
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/deployments", headers=headers)
        expected_port = 8080
        expected_ip = "estuary-deployer"
        print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorCodes.HTTP_CODE.get(Constants.SUCCESS))
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(len(body.get('description')), 2)
        self.assertEqual(len(body.get('description')[0].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[0].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[0].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/")
        self.assertEqual(len(body.get('description')[1].get("id")), 16)  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[1].get("ip_port"),
                         f"{expected_ip}:{expected_port}")  # deployment id is a 16 char word
        self.assertEqual(body.get('description')[1].get("homePageUrl"),
                         f"http://{expected_ip}:{expected_port}/")
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_getdeployments_unauthorized(self):
        xid = 'whatever'
        headers = {
            'Token': 'whateverinvalid',
            'X-Request-ID': xid
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/deployments", headers=headers)

        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertEqual(headers.get('X-Request-ID'), xid)

    def test_time_of_100_requests(self):
        repetitions = 100
        start = time.time()
        for i in range(1, repetitions):
            response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps")
            self.assertEqual(response.status_code, 200)
        end = time.time()
        print(f"made {repetitions} get eureka apps repetitions in {end - start} s")

    def test_get_agents_file_missing_file_path_n(self):
        header_key = 'File-Path'
        headers = {
            'whatever': '100'
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description')[0].get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.HTTP_HEADER_NOT_PROVIDED) % header_key)
        self.assertEqual(body.get('description')[1].get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.HTTP_HEADER_NOT_PROVIDED) % header_key)
        self.assertEqual(body.get('description')[0].get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.HTTP_HEADER_NOT_PROVIDED) % header_key)
        self.assertEqual(body.get('description')[1].get('description'),
                         ErrorCodes.HTTP_CODE.get(Constants.HTTP_HEADER_NOT_PROVIDED) % header_key)
        # self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), Constants.SUCCESS)
        self.assertIsNotNone(body.get('timestamp'))

    def test_get_agents_file_p(self):
        headers = {
            'File-Path': '/etc/hostname'
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)
        self.assertGreater(len(body.get('description')[0]), 8)
        self.assertGreater(len(body.get('description')[1]), 8)

    def test_get_agents_file_file_not_found(self):
        expected = f"Exception([Errno 2] No such file or directory:"
        headers = {
            'File-Path': '/dummy_path'
        }
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/file", headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)
        self.assertIn(expected, body.get('description')[0].get('description'))
        self.assertIn(expected, body.get('description')[1].get('description'))

    def test_agent_teststart_broadcast_p(self):
        cmds = "ls -lrt\n"
        test_id = "100"
        response = requests.post(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached/{test_id}",
                                 data=cmds)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)
        self.assertEqual(body.get('description')[0].get('description'), test_id)
        self.assertEqual(body.get('description')[1].get('description'), test_id)
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached")
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)
        self.assertEqual(body.get('description')[0].get('description').get('id'), test_id)
        self.assertEqual(body.get('description')[1].get('description').get('id'), test_id)

    def test_agent_teststart_unicast_p(self):
        test_id = ["1", "2"]
        cmds = ["echo {}".format(test_id[0]), "echo {}".format(test_id[1])]

        # get eureka apps agent
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/agent")
        # print(dump.dump_response(response))
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)

        # send unicast teststart request and check the results
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr'), item.get('port'))
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached/{test_id[i]}",
                                     data=cmds[i], headers=headers)
            body = response.json()
            print(dump.dump_response(response))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 1)
            self.assertEqual(body.get('description')[0].get('description'), test_id[i])

            response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached")
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 2)
            self.assertIn(test_id[i], [body.get('description')[0].get('description').get('id'),
                                       body.get('description')[1].get('description').get('id')])

    def test_agent_teststart_unicast_wrong_ipport_p(self):
        test_id = ["1", "2"]
        cmds = ["echo {}".format(test_id[0]), "echo {}".format(test_id[1])]

        # get eureka apps agent
        response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/eurekaapps/agent")
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body.get('description')), 2)

        # send unicast teststart request and check the results
        agent_apps = body.get('description')
        for i, item in enumerate(agent_apps):
            headers = {
                'IpAddr-Port': '{}:{}'.format(item.get('ipAddr') + "dummy", item.get('port'))
            }

            # send unicast message to the agents with the ip:port
            response = requests.post(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached/{test_id[i]}",
                                     data=cmds[i], headers=headers)
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 0)

            response = requests.get(f"http://{self.discovery_ip}:{self.server_port}/agents/commanddetached")
            body = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(body.get('description')), 2)


if __name__ == '__main__':
    unittest.main()
