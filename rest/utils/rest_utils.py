import requests


class RestUtils:

    @staticmethod
    def get(url):
        return requests.get(url, timeout=1);
