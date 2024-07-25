from bs4 import BeautifulSoup
import requests
import utils.utils
import os.path
import pandas as pd

def genre_to_csv(arr):
    RELATIVE_FILE_PATH = '../resources/csv/genre.csv'
    utils.utils.create_empty_file(RELATIVE_FILE_PATH)
    df = pd.DataFrame({
        'genre': arr
    })
    df.to_csv(
        utils.utils.get_absolute_path(RELATIVE_FILE_PATH),
        index=False,
        header=False
    )

"""
    requests considerates :
        1. proxy
        2. user-agent
        3. referer
"""
my_path = os.path.abspath(os.path.dirname(__file__))
proxy_path = os.path.join(my_path, "../../resources/http_proxies.txt")
useragent_path = os.path.join(my_path, "../../resources/useragent/useragent.txt")

proxies = utils.utils.get_proxies()
proxy = utils.utils.get_randomzied_element(proxies)
useragents = utils.utils.get_useragents()
useragent = utils.utils.get_randomzied_element(useragents)
headers = utils.utils.get_headers(useragent)

genre_requests = requests.get(
    "https://www.mangaupdates.com/genres.html",
    proxies={'http': proxy},
    headers=headers
)
soup = BeautifulSoup(genre_requests.text, 'html.parser').find('body')
genre_list = soup.find_all('div', class_=['pl-3 pt-3 pr-3 releasestitle'])

list = list(map(
    lambda soup_element: soup_element.get_text(),
         genre_list))

genre_to_csv(list)
