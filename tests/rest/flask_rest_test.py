#!/usr/bin/env python3
import os
import platform
import unittest

import requests
import yaml
from flask import json
from parameterized import parameterized
from requests_toolbelt.utils import dump

from rest.api.constants.api_constants import ApiCode
from rest.api.responsehelpers.error_codes import ErrorMessage


class FlaskServerTestCase(unittest.TestCase):
    server = "http://localhost:8080"
    # server = "http://" + os.environ.get('SERVER')

    expected_version = "4.2.2"
    cleanup_count_safe = 5

    def test_env_endpoint(self):
        response = requests.get(self.server + "/env")

        body = json.loads(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(body.get('description')), 7)
        # self.assertIsNotNone(body.get('description)["VARS_DIR"])
        # self.assertIsNotNone(body.get('description)["TEMPLATES_DIR"])
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))

    def test_ping_endpoint(self):
        response = requests.get(self.server + "/ping")

        body = json.loads(response.text)
        headers = response.headers

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'), "pong")
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_getenv_endpoint_p(self):
        env_var = "PATH"
        response = requests.get(self.server + "/env/{}".format(env_var))

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertIsNotNone(body.get('description'))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))

    @parameterized.expand([
        ("FOO1", "BAR10")
    ])
    @unittest.skipIf(os.environ.get('SKIP_ON_CENTOS') == "true", "skip on centos docker")
    def test_env_load_from_props(self, env_var, expected_value):
        response = requests.get(self.server + "/env/" + env_var)

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get("message"), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('description'), expected_value)
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))

    def test_setenv_endpoint_jsonwithvalues_p(self):
        payload = {"a": "b", "FOO1": "BAR1"}
        headers = {'Content-type': 'application/json'}

        response = requests.post(self.server + f"/env", data=json.dumps(payload),
                                 headers=headers)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('description'), payload)
        self.assertEqual(body.get("message"), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))

    def test_getenv_endpoint_n(self):
        env_var = "alabalaportocala"
        response = requests.get(self.server + "/env/{}".format(env_var))

        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get('message'),
                         ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('description'), None)
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_about_endpoint(self):
        response = requests.get(self.server + "/about")
        service_name = "estuary-discovery"
        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(body.get('description'), dict)
        self.assertEqual(body.get('name'), service_name)
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_about_endpoint_xid_set_by_client_is_same(self):
        xid = "whatever"
        headers = {
            'X-Request-ID': xid
        }
        response = requests.get(self.server + "/about", headers=headers)
        service_name = "estuary-discovery"
        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(body.get('description'), dict)
        self.assertEqual(body.get('name'), service_name)
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.SUCCESS.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.SUCCESS.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(headers.get('X-Request-ID'), xid)

    def test_about_endpoint_unauthorized(self):
        headers = {'Token': "invalidtoken"}
        response = requests.get(self.server + "/about", headers=headers)
        service_name = "estuary-discovery"
        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 401)
        self.assertEqual(body.get('description'), "Invalid Token")
        self.assertEqual(body.get('name'), service_name)
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.UNAUTHORIZED.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.UNAUTHORIZED.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_about_endpoint_options_must_be_auth(self):
        headers = {'Token': "invalidtoken"}
        response = requests.options(self.server + "/about", headers=headers)
        headers = response.headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(headers.get('X-Request-ID')), 16)

    def test_about_endpoint_unauthorized_xid_by_client_remains_the_same(self):
        xid = "whatever"
        headers = {
            'Token': "invalidtoken",
            'X-Request-ID': xid
        }
        response = requests.get(self.server + "/about", headers=headers)
        service_name = "estuary-discovery"
        body = response.json()
        headers = response.headers
        self.assertEqual(response.status_code, 401)
        self.assertEqual(body.get('description'), "Invalid Token")
        self.assertEqual(body.get('name'), service_name)
        self.assertEqual(body.get('message'), ErrorMessage.HTTP_CODE.get(ApiCode.UNAUTHORIZED.value))
        self.assertEqual(body.get('version'), self.expected_version)
        self.assertEqual(body.get('code'), ApiCode.UNAUTHORIZED.value)
        self.assertIsNotNone(body.get('timestamp'))
        self.assertIsNotNone(body.get('path'))
        self.assertEqual(headers.get('X-Request-ID'), xid)

    @unittest.skipIf(os.environ.get('TEMPLATES_DIR'),
                     "inputs/templates")  # when service runs on VM only this is skipped
    @unittest.skipIf(platform.system() == "Windows", "skip on Win")
    @unittest.skipIf(os.environ.get('SKIP_ON_CENTOS') == "true", "skip on centos docker")
    def test_swagger_endpoint(self):
        response = requests.get(self.server + "/api/docs")

        body = response.text
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.find("html") >= 0)

    def test_swagger_yml_endpoint(self):
        response = requests.get(self.server + "/swagger/swagger.yml")

        # body = yaml.safe_load(response.text)
        self.assertEqual(response.status_code, 200)
        # self.assertTrue(len(body.get('paths')) == 14)

    @parameterized.expand([
        ("json.j2", "json.json"),
        ("yml.j2", "yml.yml")
    ])
    def test_rend_endpoint_p(self, template, variables):
        response = requests.get(self.server + "/render/{}/{}".format(template, variables))

        body = yaml.safe_load(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body), 3)

    @parameterized.expand([
        ("json.j2", "doesnotexists.json"),
        ("yml.j2", "doesnotexists.yml")
    ])
    def test_rend_endpoint_no_such_variables_file_n(self, template, variables):
        expected = "Exception"

        response = requests.get(self.server + "/render/{}/{}".format(template, variables))

        body = response.json()
        self.assertEqual(response.status_code, 500)
        # self.assertEqual(expected, body.get("description"))
        self.assertIn(expected, body.get("description"))

    @parameterized.expand([
        ("doesnotexists.j2", "json.json"),
        ("doesnotexists.j2", "yml.yml")
    ])
    def test_rend_endpoint_no_such_template_file_n(self, template, variables):
        expected = f"Exception"

        response = requests.get(self.server + "/render/{}/{}".format(template, variables))

        body = response.json()
        self.assertEqual(response.status_code, 500)
        self.assertIn(expected, body.get("description"))

    @parameterized.expand([
        ("standalone.yml", "variables.yml")
    ])
    def test_rendwithenv_endpoint(self, template, variables):
        payload = {'DATABASE': 'mysql56', 'IMAGE': 'latest'}
        headers = {'Content-type': 'application/json'}

        response = requests.post(self.server + f"/render/{template}/{variables}", data=json.dumps(payload),
                                 headers=headers)

        print(dump.dump_response(response))
        self.assertEqual(response.status_code, 200)
        body = yaml.safe_load(response.text)
        self.assertEqual(len(body.get("services")), 2)
        self.assertEqual(int(body.get("version")), 3)


if __name__ == '__main__':
    unittest.main()
