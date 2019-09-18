import threading

import requests


class ThreadUtils:
    response_list = []
    urls = []

    def __init__(self):
        pass

    def set_urls(self, urls):
        self.urls = urls

    def get_request(self, url):
        try:
            response = requests.get(url, timeout=1)
            body = response.json()
            self.response_list.append("ceva")
        except:
            pass

    def get_list(self):
        return self.response_list

    def spawn(self):
        threads = [threading.Thread(target=self.get_request, args=(url,)) for url in self.urls]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()