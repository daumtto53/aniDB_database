import queue
import threading
import time
from datetime import datetime


import requests

q = queue.Queue()
valid_proxies = []
# with open("./resources/http_proxies.txt", "r") as f :
with open("./resources/http_proxies_speedx", "r") as f :
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)

def check_proxies(url) :
    global q
    while not q.empty() :
        print("check_proxies")
        proxy = q.get()

        proxies={
            "http": proxy,
            # "https": proxy,
        }

        try:
            res = requests.get(url, proxies=proxies, timeout=10)
        except:
            print("could not connect")
            continue
        if res.status_code == 200:
            print(f"could connect = {proxy}")
            valid_proxies.append(proxy)
        time.sleep(2)

working_threads = []

check_proxies("https://myanimelist.net/manga/13/One_Piece")

# for _ in range(10) :
#     thread = threading.Thread(target=check_proxies, args=("https://myanimelist.net/anime/35343/Menhera_Ayuri_no_Yamanai_Onedari__Headphone_wa_Hazusenai",))
#     thread.start()
#     working_threads.append(thread)

for t in working_threads :
    print(123)
    # t.join()


print(f"valid proxies = {len(valid_proxies)}")
for proxy in valid_proxies:
    print(proxy)
with open("./resources/working_proxies" + datetime.now().strftime("%YY%mm%dd_%HH%MM") + ".txt", "w+") as f :
    for proxy in valid_proxies:
        f.write(proxy)
        f.write("\n")
