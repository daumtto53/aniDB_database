"""
    양식 : type=manga, perpage=100, letter=[A-Z][A-Z]
"""
# https://www.mangaupdates.com/series.html?type=manga&perpage=100&letter=AA&display=list  AND
# https://www.mangaupdates.com/series.html?page=21&type=manga&perpage=100&display=list (page=1~21)

import queue
import re
import threading

import requests
import utils.utils
import os.path
import pandas as pd

import logging
import sys

from bs4 import BeautifulSoup

# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scrape_manga_links.log", mode="w", encoding='utf-8'),
    ],
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

my_path = os.path.abspath(os.path.dirname(__file__))
proxy_path = os.path.join(my_path, "../../resources/http_proxies.txt")
useragent_path = os.path.join(my_path, "../../resources/useragent/useragent.txt")

proxies = utils.utils.get_proxies()
proxy = utils.utils.get_randomzied_element(proxies)
useragents = utils.utils.get_useragents()
useragent = utils.utils.get_randomzied_element(useragents)
headers = utils.utils.get_headers(useragent)
logging.info(f'proxies={proxy}, userAgent={useragent}, userheader={headers}')


def queue_parsed_urls_into_data_queue(urls):
    global data_queue
    for url in urls:
        data_queue.put(url)


def create_consuming_urls():
    retrieval_url = []
    url_q = queue.Queue()
    for i in range(26):
        for j in range(26):
            prefix_ = chr(ord('A') + i)
            postfix_ = chr(ord('A') + j)
            str_ = prefix_ + postfix_
            url = f'https://www.mangaupdates.com/series.html?type=manga&perpage=100&letter={str_}&display=list'
            retrieval_url.append(url)
            url_q.put(url)

            #PRACICING
            if j == 5:
                return retrieval_url, url_q

    for i in range(21):
        url = f'https://www.mangaupdates.com/series.html?page={i+1}&type=manga&perpage=100&display=list'
        retrieval_url.append(url)
        url_q.put(url)
    for i, e in enumerate(retrieval_url):
        print(f'{i} : {e}')
    return retrieval_url, url_q


def create_queue_from_consuming_urls(consuming_urls):
    url_q = queue.Queue()
    for item in consuming_urls:
        url_q.put(item)
    return url_q


#
(consuming_urls, url_queue) = create_consuming_urls()
links_to_retry_queue = queue.Queue()
data_queue = queue.Queue()

threads = []
num_threads = 12
thread_index = 0

def scrape_manga_links_thread_starter():
    global threads

    # start 10 functions w/ time interval
    for i in range(num_threads):
        thread = threading.Thread(target=scrape_manga_links)
        threads.append(thread)
        thread.start()
        utils.utils.sleep_random_time(3,10)

    for thread in threads:
        thread.join()
    save_manga_links(data_queue)
    save_error_link_to_retry(links_to_retry_queue)


def scrape_manga_links():
    global url_queue
    global data_queue

    while not url_queue.empty():
        thread_headers = utils.utils.get_headers(useragent)
        thread_proxy = utils.utils.get_randomzied_element(proxies)
        link = url_queue.get()
        req = requests.get(
            link,
            proxies={'http': thread_proxy},
            headers=thread_headers
        )

        try:
            logging.info(f'########## {link} SCRAPING START ############')
            soup = BeautifulSoup(req.content, 'html.parser')

            divs = soup.find_all('div', {'class': 'col-6 py-1 py-md-0 text'}) + soup.find_all('div', {'class': 'col-6 py-1 py-md-0 text alt'})
            for i, div in enumerate(divs):
                href = div.find('a')['href']
                data_queue.put(href)
                print(f'{i}: {href}')

            utils.utils.sleep_random_time(45,70)
            logging.info(f'########## {link} SCRAPING END ############')

        # request 에러 ==
        except requests.exceptions.RequestException as e:
            logging.warning(f"REQUEST EXCEPTION : STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            thread_proxy = utils.utils.get_randomzied_element(proxies)
            continue
        except requests.exceptions.MissingSchema as e:
            links_to_retry_queue.put(link)
            logging.warning(f"URLEMPTYERROR: STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            continue
        except AttributeError as e:
            links_to_retry_queue.put(link)
            logging.warning(f"ATTRIBUTEERROR: STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            continue
        except KeyboardInterrupt as e:
            logging.warning(f"CTRL C INPUT KEYBOARD INTERUUPTION TRIGGERED!!!!!!!!!!!, e={e}")
            save_manga_links(data_queue)
            save_error_link_to_retry(links_to_retry_queue)
        except Exception as e:
            links_to_retry_queue.put(link)
            logging.warning(f'WARNING: {e}')
            continue


# 안돌아가는 오류가 있음. 나중에 Test 해볼 것.
def save_error_link_to_retry(q):
    logging.info(f"SAVING ERROR to file...")
    RELATIVE_FILE_PATH = '../resources/error/manga_link_error_link.txt'
    path = utils.utils.get_absolute_path(RELATIVE_FILE_PATH)

    with open(path, mode="w+") as f:
        while not q.empty():
            link = q.get()
            f.write(f"{link}\n")
            logging.info(f'SAVING ERROR TO FILE = {link}')
    logging.info(f"SAVING ERROR to file... FINISHED")

def save_manga_links(q):
    logging.info(f"SAVING MANGA LINKS to file...")
    RELATIVE_FILE_PATH = '../resources/mangaupdates/manga_link.txt'
    path = utils.utils.get_absolute_path(RELATIVE_FILE_PATH)
    with open(path, mode="w+") as f:
        while not q.empty():
            link = q.get()
            f.write(f"{link}\n")
            logging.info(f'SAVING URL TO FILE = {link}')
    logging.info(f"SAVING MANGA LINKS to file... FINISHED")


def practice():
    global url_queue
    global data_queue

    thread_headers = utils.utils.get_headers(useragent)
    thread_proxy = utils.utils.get_randomzied_element(proxies)
    link = "https://www.mangaupdates.com/series.html?page=21&type=manga&perpage=100&display=list"
    req = requests.get(
        link,
        proxies={'http': thread_proxy},
        headers=thread_headers
    )

    logging.info(f'########## {link} SCRAPING START ############')
    soup = BeautifulSoup(req.content, 'html.parser')
    divs = soup.find_all('div', {'class': 'col-6 py-1 py-md-0 text'}) + soup.find_all('div', {'class': 'col-6 py-1 py-md-0 text alt'})
    for i, div in enumerate(divs):
        href = div.find('a')['href']
        data_queue.put(href)
        print(f'{i}: {href}')

    utils.utils.sleep_random_time(45,70)
    logging.info(f'########## {link} SCRAPING END ############')

# practice()

scrape_manga_links_thread_starter()
