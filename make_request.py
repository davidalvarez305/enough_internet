import os
import random
import ssl
from urllib import request


def make_request(source_url):
    ssl._create_default_https_context = ssl._create_unverified_context
    username = os.environ.get('P_USER')
    password = os.environ.get('P_PASSWORD')
    port = int(os.environ.get('P_PORT'))
    url = os.environ.get('P_URL')
    session_id = random.random()
    super_proxy_url = ('http://%s-country-us-session-%s:%s@%s:%d' %
                       (username, session_id, password, url, port))
    proxy_handler = request.ProxyHandler({
        'http': super_proxy_url,
        'https': super_proxy_url,
    })

    opener = request.build_opener(proxy_handler)

    resp = opener.open(source_url).read().decode("utf-8")

    return resp
