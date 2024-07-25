import threading
import logging
import sys

from bs4 import BeautifulSoup
import requests
import utils.utils
import os.path
import pandas as pd

import queue

# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scrape_publishers.log", mode="w"),
    ],
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
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

processed_publisher_list = []

def get_publisher_links():
    with open("../../resources/mangaupdates/publisher_links.txt") as f:
        links = f.read().split("\n")
    return links


links = get_publisher_links()

links_queue = queue.Queue()
for link in links:
    links_queue.put(link)

links_to_retry = queue.Queue()
data_queue = queue.Queue()

threads = []
num_threads = 12
thread_index = 0


def scrape_publisher_thread_starter():
    global threads

    # start 10 functions w/ time interval
    for i in range(num_threads):
        thread = threading.Thread(target=scrape_publisher_thread)
        threads.append(thread)
        thread.start()
        utils.utils.sleep_random_time(3,10)

    for thread in threads:
        thread.join()
    print()
    save_publisher_queue_data_to_csv(data_queue)
    save_error_link_to_retry(links_to_retry)


def scrape_publisher_thread():
    global links_queue
    global data_queue

    while not links_queue.empty():
        thread_headers = utils.utils.get_headers(useragent)
        thread_proxy = utils.utils.get_randomzied_element(proxies)
        link = links_queue.get()
        publisher_request = requests.get(
            link,
            proxies={'http': thread_proxy},
            headers=thread_headers
        )

        # get_alternate_names
        try:
            soup = BeautifulSoup(publisher_request.text, 'html.parser').find('body')

            title_name = soup.find("span", {"class": "releasestitle tabletitle"}).get_text().strip()
            # print(title_name)
            logging.info(f"LINK={link}, TITLE_NAME={title_name}")

            alternate_name_string = soup.find("div", {"class": "sContent"}).get_text('\n').split('\n')
            alternate_name_string = list(filter(None, alternate_name_string))
            # print(alternate_name_string)
            logging.info(f"LINK={link}, Link={link}")

            type = soup.find_all("div", {"class": "sContent"})[1].get_text().strip()
            logging.info(f"LINK={link}, type={type}")
            # print(type)

            website_url = soup.find_all("div", {"class": "sContent"})[3].find('a', href=True)
            if website_url is not None:
                website_url = website_url['href']
            else:
                website_url = ''
            # print(website_url)
            logging.info(f"LINK={link}, website_url={website_url}")


            utils.utils.sleep_random_time(20,60)

            data_queue.put({
                'title': title_name,
                'publisher_names': alternate_name_string,
                'type': type,
                'website_url': website_url
            })

        # request 에러 ==
        except requests.exceptions.RequestException as e:
            logging.WARNING(f"REQUEST EXCEPTION : STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            thread_proxy = utils.utils.get_randomzied_element(proxies)
            continue
        except TypeError as e:
            logging.WARNING(f"TYPEERROR : STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            thread = threading.Thread(target=scrape_publisher_thread)
            threads.append(thread)
            thread.start()
            thread.join()
            utils.utils.sleep_random_time(5, 15)
            #write
            links_to_retry.put(link)
            continue
        except requests.exceptions.MissingSchema as e:
            logging.WARNING(f"URLEMPTYERROR: STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
        except AttributeError as e:
            logging.WARNING(f"ATTRIBUTEERROR: STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")



def save_error_link_to_retry(q):
    logging.info(f"Saving ERROR to file...")
    RELATIVE_FILE_PATH = '../resources/error/publisher_error_link.txt'
    path = utils.utils.get_absolute_path(RELATIVE_FILE_PATH)

    with open(path, mode="a+") as f:
        while q.empty():
            link = q.get()
            f.write(f"{link}\n")
    logging.info(f"Saving ERROR to file... FINISHED")


def save_publisher_queue_data_to_csv(q):
    logging.info(f"Saving PUBLISHER to file...")
    RELATIVE_FILE_PATH = '../resources/csv/publishers.csv'

    # queue elements of dictionary object -> array
    # dictlist = list(q)
    dictlist = []
    while not q.empty():
        dictlist.append(q.get())

    title = [data['title'] for data in dictlist]
    publisher_names = [data['publisher_names'] for data in dictlist]
    types = [data['type'] for data in dictlist]
    website_url = [data['website_url'] for data in dictlist]

    df = pd.DataFrame({
        'title': title,
        'alternate_name': publisher_names,
        'type': types,
        'website_url': website_url
    })

    df.to_csv(
        utils.utils.get_absolute_path(RELATIVE_FILE_PATH),
        index=False,
        header=False
    )
    logging.info(f"Saving PUBLISHER to file... FINISHED")


def save_publisher_data_to_csv(dict):
    RELATIVE_FILE_PATH = '../resources/csv/publishers.csv'
    utils.utils.create_empty_file(RELATIVE_FILE_PATH)

    title = [data['title'] for data in dict]
    publisher_names = [data['publisher_names'] for data in dict]
    type = [data['type'] for data in dict]
    website_url = [data['website_url'] for data in dict]

    df = pd.DataFrame({
        'title': title,
        'alternate_name': publisher_names,
        'type': type,
        'website_url': website_url
    })

    df.to_csv(
        utils.utils.get_absolute_path(RELATIVE_FILE_PATH),
        index=False,
        header=False
    )



def process_all_publishers(links):
    data_to_save = []

    for index, link in enumerate(links):
        publisher_request = requests.get(
            link,
            proxies={'http': proxy},
            headers=headers
        )
        try:
            print('#######################')
            soup = BeautifulSoup(publisher_request.text, 'html.parser').find('body')
            title_name = soup.find("span", {"class": "releasestitle tabletitle"}).get_text().strip()
            print(title_name)

            alternate_name_string = soup.find("div", {"class": "sContent"}).get_text('\n').split('\n')
            alternate_name_string = list(filter(None, alternate_name_string))
            print(alternate_name_string)

            type = soup.find_all("div", {"class": "sContent"})[1].get_text().strip()
            print(type)

            website_url = soup.find_all("div", {"class": "sContent"})[3].find('a', href=True)
            if website_url is not None:
                website_url = website_url['href']
            else:
                website_url = ''
            print(website_url)
            utils.utils.sleep_random_time(5, 10)

            data_to_save.append({
                'title': title_name,
                'publisher_names': alternate_name_string,
                'type': type,
                'website_url': website_url
            })
            print('#######################')

        except requests.exceptions.RequestException:
            print(f"{requests.Request}, final_link: {link}")
            save_publisher_data_to_csv(data_to_save)



def process_one_publisher(link):
    publisher_request = requests.get(
        link,
        proxies={'http': proxy},
        headers=headers
    )

    # get_alternate_names
    try:
        soup = BeautifulSoup(publisher_request.text, 'html.parser').find('body')

        title_name = soup.find("span", {"class": "releasestitle tabletitle"}).get_text().strip()
        print(title_name)

        alternate_name_string = soup.find("div", {"class": "sContent"}).get_text('\n').split('\n')
        alternate_name_string = list(filter(None, alternate_name_string))
        print(alternate_name_string)

        type = soup.find_all("div", {"class": "sContent"})[1].get_text().strip()
        print(type)

        website_url = soup.find_all("div", {"class": "sContent"})[3].find('a', href=True)
        website_url = website_url['href']
        print(website_url)
        utils.utils.sleep_random_time(3, 6)

        data_to_save = []
        data_to_save.append({
            'title': title_name,
            'publisher_names': alternate_name_string,
            'type': type,
            'website_url': website_url
        })
        save_publisher_data_to_csv(data_to_save)

    except requests.exceptions.RequestException:
        print(f"{requests.Request}, final_link: {link}")




# process_one_publisher("https://www.mangaupdates.com/publisher/rmcy4fo/shogakukan")
# process_all_publishers(links)

scrape_publisher_thread_starter()
