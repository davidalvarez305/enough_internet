import json
import random
import ssl
from urllib import request

from constants import CREDENTIALS_DIR


def make_request(source_url):
    env_file = open(CREDENTIALS_DIR + "env.json")
    env = json.load(env_file)
    ssl._create_default_https_context = ssl._create_unverified_context
    username = env.get('P_USER')
    password = env.get('P_PASSWORD')
    port = int(env.get('P_PORT'))
    url = env.get('P_URL')
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
