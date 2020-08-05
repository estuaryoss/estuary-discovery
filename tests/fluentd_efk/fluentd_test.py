import unittest

import requests
from requests_toolbelt.utils import dump


class FluentdEFKTestCase(unittest.TestCase):
    server = "http://localhost:9200"  # elasticsearch

    def test_number_of_ES_messages(self):
        # total-3 estuary stack
        # 3 messages each microservice boot
        # 8 messages api request-response
        # 3 fluentd booting
        # 3 from java agent
        expected_no_of_ES_messages = (1 + 1 + 1) + (2 + 2 + 2 + 2) + (1 + 1 + 1) + (2 + 1)
        response = requests.get(self.server + "/fluentd*/_search?size=1000&&sort=@timestamp")

        body = response.json()
        number_of_ES_messages = body.get("hits").get("total").get("value")

        print(dump.dump_response(response))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(number_of_ES_messages, expected_no_of_ES_messages)


if __name__ == '__main__':
    unittest.main()
