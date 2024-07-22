import time
import random

def get_useragents() :
    useragent = []
    with open('../resources/useragent/useragent.txt', "r") as f:
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

def get_proxies(dir):
    with open("../resources/http_proxies.txt") as f:
        proxies = f.read().split("\n")
        return proxies
