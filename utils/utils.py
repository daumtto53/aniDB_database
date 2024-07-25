import time
import random
import os.path

current_path = os.path.abspath(os.path.dirname(__file__))
useragent_path = "../resources/useragent/useragent.txt"
http_proxy_path = "../resources/http_proxies.txt"
https_proxy_path = "../resources/https/https_proxies_general.txt"


def get_absolute_path(relative_path):
    return os.path.join(current_path, relative_path)


def create_empty_file(relative_path):
    path = get_absolute_path(relative_path)
    with open(path, 'w') as fp:
        pass


def get_useragents() :
    useragent_fullpath = get_absolute_path(useragent_path)

    useragent = []
    with open(useragent_fullpath, "r") as f:
        useragents = f.read().split('\n')
        for agent in useragents:
            useragent.append(agent)
    return useragent


def get_random_useragent_internally():
    useragents = get_useragents()
    random_index = int(random.uniform(0, len(useragents) - 1))
    return useragents[random_index]


def get_random_useragent(useragents):
    random_index = int(random.uniform(0, len(useragents) - 1))
    return useragents[random_index]


# 10 <= start, finish <= n
def sleep_random_time(start, finish):
    if start <= 10:
        print("SLEEP OVER 10 SEC OR MORE")
        return 20
    randomized_interval = random.uniform(start, finish)
    time.sleep(randomized_interval)

# def get_random_proxy(proxy):
#     with open('')


def get_proxies():
    http_proxy_full_path = get_absolute_path(http_proxy_path)
    with open(http_proxy_full_path, 'r') as f:
        proxies = f.read().split("\n")
        return proxies


def get_https_proxies():
    print(https_proxy_path)
    https_proxy_full_path = get_absolute_path(https_proxy_path)
    with open(https_proxy_full_path, 'r', encoding='utf-8') as f:
        proxies = f.read().split("\n")
        return proxies


def get_randomzied_element(arr):
    return arr[int(random.uniform(0, len(arr)))]


def get_headers(useragent):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5,zh-TW;q=0.4,zh;q=0.3",
        "User-Agent": useragent
    }
    return headers
