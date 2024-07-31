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
from langdetect import detect

from mangaupdates.NovelInfo import NovelInfo


MANGA_INFO_BATCH = 0


# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"scrape_manga_info_batch_{MANGA_INFO_BATCH}.log", mode="w", encoding='utf-8'),
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


def get_novel_info_links():
    with open(f"../../resources/mangaupdates/manga_link_batch_{MANGA_INFO_BATCH}.txt") as f:
        links = f.read().split('\n')
    return links

links = get_novel_info_links()

data_queue = queue.Queue()
links_to_retry_queue = queue.Queue()
links_queue = queue.Queue()
for link in links:
    links_queue.put(link)

threads = []
num_threads = 4
thread_index = 0


def iterate_over_batch_files():
    global links
    global data_queue
    global links_to_retry_queue
    global links_queue
    global MANGA_INFO_BATCH

    for i in range(79 + 1):
        MANGA_INFO_BATCH = i

        # LOGGING
        logger = logging.getLogger(__name__)
        logging.basicConfig(
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"scrape_manga_info_batch_{MANGA_INFO_BATCH}.log", mode="w", encoding='utf-8'),
            ],
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        if i == 0 or i == 1:
            logging.info(f"SKIPPING batch_i={i}")
            continue

        logging.info(f'WORKING ON BATCH ={i}')
        links = get_novel_info_links()
        data_queue = queue.Queue()
        links_to_retry_queue = queue.Queue()
        links_queue = queue.Queue()

        for url in links:
            links_queue.put(url)
        scrape_novel_info_thread_starter()


def scrape_novel_info_thread_starter():
    global threads

    # start 10 functions w/ time interval
    for i in range(num_threads):
        thread = threading.Thread(target=scrape_novel_info_thread)
        threads.append(thread)
        thread.start()
        utils.utils.sleep_random_time(8, 20)

    for thread in threads:
        thread.join()
    save_publisher_queue_data_to_csv(data_queue)
    save_error_link_to_retry(links_to_retry_queue)


def scrape_novel_info_thread():
    global links_queue
    global data_queue

    while not links_queue.empty():
        novel_info = NovelInfo()
        thread_headers = utils.utils.get_headers(useragent)
        thread_proxy = utils.utils.get_randomzied_element(proxies)
        link = links_queue.get()
        req = requests.get(
            link,
            proxies={'http': thread_proxy},
            headers=thread_headers
        )

        # get_alternate_names
        try:
            logging.info(f'########## {link} SCRAPING START ############')
            # Re:Zero Kara Hajimeru Isekai Seikatsu (Novel)
            soup = BeautifulSoup(req.content, 'html.parser')
            #TITLE
            set_novel_info_title(novel_info, soup)
            to_parse_list = soup.find_all("div", {"class": "sContent"})

            set_novel_info_description(novel_info, to_parse_list[0])
            set_novel_info_type(novel_info, to_parse_list[1])
            set_novel_info_related_series(novel_info, to_parse_list[2])
            set_novel_info_associated_names(novel_info, to_parse_list[3])
            set_novel_info_status_in_origin_country(novel_info, to_parse_list[6])
            set_novel_info_anime_start_end(novel_info, to_parse_list[8])
            set_novel_info_image_url(novel_info, to_parse_list[13])
            set_novel_info_genre(novel_info,to_parse_list[14] )
            set_novel_info_authors(novel_info, to_parse_list[18])
            set_novel_info_artists(novel_info,to_parse_list[19] )
            set_novel_info_year(novel_info, to_parse_list[20])
            set_novel_info_original_publisher(novel_info, to_parse_list[21])
            set_novel_info_serialized_in(novel_info, to_parse_list[22])

            utils.utils.sleep_random_time(15,35)

            data_queue.put(novel_info)
            logging.info(f'MANGA_INFO = {novel_info}')
            logging.info(f'########## {link} SCRAPING END ############')

        # request 에러 ==
        except requests.exceptions.RequestException as e:
            logging.warning(f"REQUEST EXCEPTION : STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            thread_proxy = utils.utils.get_randomzied_element(proxies)
            continue
        except TypeError as e:
            logging.warning(f"TYPEERROR : STATUS={requests.status_codes.codes}, final_link: {link}, PROXY={thread_proxy} ERROR: {e}")
            # thread = threading.Thread(target=scrape_novel_info_thread())
            # threads.append(thread)
            # thread.start()
            # thread.join()
            # utils.utils.sleep_random_time(5, 15)
            #write
            links_to_retry_queue.put(link)
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
            save_publisher_queue_data_to_csv(data_queue)
            save_error_link_to_retry(links_to_retry_queue)
        except Exception as e:
            links_to_retry_queue.put(link)
            logging.warning(f'WARNING: {e}')
            continue


# 안돌아가는 오류가 있음. 나중에 Test 해볼 것.
def save_error_link_to_retry(q):
    logging.info(f"SAVING ERROR to file...")
    RELATIVE_FILE_PATH = f'../resources/error/manga_info_batch_{MANGA_INFO_BATCH}_error_link.txt'
    path = utils.utils.get_absolute_path(RELATIVE_FILE_PATH)

    with open(path, mode="w+") as f:
        while not q.empty():
            link = q.get()
            f.write(f"{link}\n")
            logging.info(f'SAVING ERROR TO FILE = {link}')
    logging.info(f"SAVING ERROR to file... FINISHED")


def save_publisher_queue_data_to_csv(q):
    logging.info(f"SAVING MANGA INFO to file...")
    RELATIVE_FILE_PATH = f'../resources/csv/manga_info_batch_{MANGA_INFO_BATCH}.csv'

    # queue elements of dictionary object -> array
    # dictlist = list(q)
    novel_info_list = []
    while not q.empty():
        novel_info_list.append(q.get())
    logging.info(f'printing MANGAINFO = {novel_info_list}')

    title = [novel_info.title for novel_info in novel_info_list]
    description = [novel_info.description for novel_info in novel_info_list]
    type_ = [novel_info.type for novel_info in novel_info_list]
    year = [novel_info.year for novel_info in novel_info_list]
    related_series = [novel_info.related_series for novel_info in novel_info_list]
    associated_names = [novel_info.associated_names for novel_info in novel_info_list]
    status_in_origin_country= [novel_info.status_in_origin_country for novel_info in novel_info_list]
    image_url= [novel_info.image_url for novel_info in novel_info_list]
    artists = [novel_info.artists for novel_info in novel_info_list]
    authors= [novel_info.authors for novel_info in novel_info_list]
    original_publisher = [novel_info.original_publisher  for novel_info in novel_info_list]
    serialized_in = [novel_info.serialized_in  for novel_info in novel_info_list]
    genres = [novel_info.genres  for novel_info in novel_info_list]
    anime_start_and_end = [novel_info.anime_start_and_end  for novel_info in novel_info_list]

    df = pd.DataFrame({
        'title': title,
        'description': description,
        'type': type_,
        'year': year,
        'related_series': related_series,
        'associated_names': associated_names,
        'status_in_origin_country': status_in_origin_country,
        'image_url': image_url,
        'artists': artists,
        'authors': authors,
        'original_publisher': original_publisher,
        'serialized_in': serialized_in,
        'genres': genres,
        'anime_start_and_end': anime_start_and_end
    })

    df.to_csv(
        utils.utils.get_absolute_path(RELATIVE_FILE_PATH),
        index=False,
        header=False
    )
    logging.info(f"Saving PUBLISHER to file... FINISHED")


"""
    #### sContent sequence ####
    0. Description
    1. Type
    2. Related_series
    3. Associated_names
    6. Status in Country of Origin
    8. Anime start, end
    13. Inage URL
    14. Genre
    18. Authors
    19. Artist
    20. Year
    21. Original_Publisher
    22. Serialized_in
    
"""
def read_practice_html():

    novel_info = NovelInfo()

    # with open("../../practice/rezero.html", 'r', encoding='utf-8') as f:
    #     html = f.read()

    headers = utils.utils.get_headers(useragent)
    proxy = utils.utils.get_randomzied_element(proxies)
    # link = "https://www.mangaupdates.com/series/3dzd5bx/noragami"
    # link = "https://www.mangaupdates.com/series/iic9jn7/99-way-to-keep-poor-life-with-onii-chan-novel"
    # link = "https://www.mangaupdates.com/series/5zlki4e/omae-gotoki-ga-maou-ni-kateru-to-omou-na-to-yuusha-party-o-tsuihou-sareta-node-outo-de-kimama-ni-kurashitai-novel"
    # link = "https://www.mangaupdates.com/series/3p2lq8p/66-666-years-advent-of-the-dark-mage-novel"
    # link = "https://www.mangaupdates.com/series/xt29hih/1-2-prince-novel"
    link = "https://www.mangaupdates.com/series/su6blie/vagabond"
    req = requests.get(
        link,
        proxies={'http': proxy},
        headers=headers
    )

    # Re:Zero Kara Hajimeru Isekai Seikatsu (Novel)
    soup = BeautifulSoup(req.content, 'html.parser')
    # soup = BeautifulSoup(html, 'html.parser')

    set_novel_info_title(novel_info, soup)
    #
    to_parse_list = soup.find_all("div", {"class": "sContent"})

    # for i, e in enumerate(to_parse_list):
    #     print(f"{i} === {e}")

    set_novel_info_description(novel_info, to_parse_list[0])
    set_novel_info_type(novel_info, to_parse_list[1])
    set_novel_info_related_series(novel_info, to_parse_list[2])
    set_novel_info_associated_names(novel_info, to_parse_list[3])
    set_novel_info_status_in_origin_country(novel_info, to_parse_list[6])
    set_novel_info_anime_start_end(novel_info, to_parse_list[8])
    set_novel_info_image_url(novel_info, to_parse_list[13])
    set_novel_info_genre(novel_info,to_parse_list[14] )
    set_novel_info_authors(novel_info, to_parse_list[18])
    set_novel_info_artists(novel_info,to_parse_list[19] )
    set_novel_info_year(novel_info, to_parse_list[20])
    set_novel_info_original_publisher(novel_info, to_parse_list[21])
    set_novel_info_serialized_in(novel_info, to_parse_list[22])




def set_novel_info_title(novel_info, soup):
    # title 처리
    title = soup.find("span", {"class": "releasestitle tabletitle"}).get_text()
    novel_info.set_title(title)
    logging.info(f"TITLE={novel_info.title}")

def set_novel_info_description(novel_info, soup):
    desc = ''
    if soup.find("div", {"id": "div_desc_more"}):
        desc = soup.find("div", {"id": "div_desc_more"}).get_text().strip()
    else:
        desc = soup.get_text().strip()
        if desc == 'N/A':
            desc = ''
    novel_info.set_description(desc)
    logging.info(f"DESC={novel_info.description}")

def set_novel_info_type(novel_info, soup):
    novel_info.set_type(soup.get_text().strip())
    logging.info(f"TYPE={novel_info.type}")

# What if N/A
def set_novel_info_related_series(novel_info, soup):
    related_series_list = []
    # related_series = list(map(lambda a_element: a_element.get_text().strip(), a_list))
    for a_tag in soup.find_all('a'):
        related_series = a_tag.get_text().strip()
        type_info = a_tag.next_sibling.strip()
        process = related_series + ' ' + type_info

        pattern = re.compile(r'^(.*?)(?:\s*\((Novel)\))?(?:,?\s*\((.*?)\))?$')
        match = pattern.match(process)

        related_series_title = match.group(1).strip() if match.group(1) else None
        related_series_type = match.group(2).strip() if match.group(2) else 'Manga'
        related_series_relation = match.group(3).strip() if match.group(3) else None
        related_series_list.append({
            'title': related_series_title,
            'type': related_series_type,
            'relation': related_series_relation,
        })
    novel_info.set_related_series(related_series_list)
    logging.info(f'RELATED_SERIES = {related_series_list}')


# What if N/A
def set_novel_info_associated_names(novel_info, soup):
    associated_names_list = []
    associated_names_list.append({
        'title': novel_info.title,
        'language': 'en'
    })
    associated_names = [text.strip() for text in soup.stripped_strings]
    # N/A
    if associated_names[0] == 'N/A':
        novel_info.set_associated_names([{
            'title': '',
            'language': '',
        }])
        logging.info(f"ASSOCIATED_NAMES={novel_info.associated_names} [[ title = {novel_info.title} ]]")
        return

    for e in associated_names:
        e = e.strip()
        pattern = re.compile(r'^(.*?)(?:\s*(\(.*\)))?$')
        match = pattern.match(e)

        associated_name = match.group(1).strip()
        if (associated_name is not None):
            language_detected = detect(associated_name)
            logging.debug(f'associated_name = {associated_name}, language={language_detected}')

        associated_names_list.append({
            'title': associated_name,
            'language': language_detected,
        })

    novel_info.set_associated_names(associated_names_list)
    # find korean and swap titles with it
    for e in associated_names_list:
        if e['language'] == 'ko':
            ko_pattern = re.compile(
                r'(?:[\uac00-\ud7af]|[\u1100-\u11ff]|[\u3130-\u318f]|[\ua960-\ua97f]|[\ud7b0-\ud7ff])+')
            pattern_match = ko_pattern.match(e['title'])
            if pattern_match:
                novel_info.set_title(e['title'])
            else:
                continue
    logging.info(f"ASSOCIATED_NAMES={novel_info.associated_names} [[ title = {novel_info.title} ]]")


# What if N/A
def set_novel_info_status_in_origin_country(novel_info, soup):
    volume = 0
    status = ''

    text_content = soup.get_text(separator='\n').strip()
    pattern = re.compile(r'(?:(\d+)\s*)Volumes?\s*\((.*)\)|(Oneshot)\s*\((.*)\)')
    matches = pattern.findall(text_content)

    for match in matches:
        logging.debug(f"match={match}")
        if match[0] != '':
            volume = int(match[0])
            status = match[1]
        if match[2] != '':
            volume = 1
            status = match[3]
    novel_info.set_status_in_origin_country({
        'volume': volume,
        'status': status
    })
    logging.info(f'STATUS_IN_ORIGINAL_COUNTRY={novel_info.status_in_origin_country}')


"""
    Starts at Vol 1 (S1) / Vol 5 (S2) / Vol 11 (Movie)
    Ends at Vol 4 (S1) / Vol 7 (S2) / Vol 13 (Movie) - Skip Vol 8-10

    Starts at Vol 1,Chap 1 (S1) | Vol 6,Chap 14 (S2)
    Ends at Vol 6,Chap 13 (S1) | Vol 13,Chap 34 (S2)

    Starts at Vol 1, Chap 1

    Starts at Vol 1, Chap 1 (S1)
    Ends at Vol 22, Chap 222 (S4 has many omissions)

    Starts at Vol 1, Chap 1
    Ends at Vol 14

    Starts at Vol 1 (S1) / Vol 6 (Movie)
    Ends at Vol 3 (S1) / Vol 6 (Movie) - Skip Vol 4-5

    Vol\s*(\d+)(?:,|.*?)(?:\(S(\d+).*?\)|\((.*)\))|Vol\s*(\d+) vs N/A
    OR
    Vol\s*(\d+)(?:,|.*?)(?:\((S\d+|Movie).*?\))|Vol\s*(\d+) vs N/A
    Vol 1 
    
"""
# What if N/A
def set_novel_info_anime_start_end(novel_info, soup):
    novel_anime_premire_list = []
    logging.debug(f'soup: get_anime_start_end = {soup.get_text()}')
    if soup.get_text() == 'N/A':
        novel_info.set_anime_start_and_end([])
        logging.info(f'MANGA_ANIME_START_AND_END = {novel_anime_premire_list}')
        return
    text_content = soup.get_text(separator='\n').split('\n')
    logging.debug(f'text_content={text_content}')
    if len(text_content) != 3:
        novel_info.set_anime_start_and_end([])
        logging.info(f'MANGA_ANIME_START_AND_END = {novel_anime_premire_list}')
        return
    starts_at_text = text_content[0]
    ends_at_text = text_content[1]
    logging.debug(f'starts_at={starts_at_text}, ends_at={ends_at_text}')

    # 분리하다.
    season_num = 0
    pattern = re.compile(r'Vol\s*(\d+)(?:,|.*?)(?:\((S\d+|Movie).*?\))|Vol\s*(\d+)')
    start_arr = pattern.findall(starts_at_text)
    end_arr = pattern.findall(ends_at_text)
    season_num = min(len(start_arr), len(end_arr))
    logging.debug(f'season_num = {season_num}')
    logging.debug(f'start_arr = {start_arr}, season_num = {season_num}')
    logging.debug(f'end_arr = {end_arr}, season_num = {season_num}')

    for index in range(0, season_num):
        volume_start = start_arr[index][0]
        volume_end = end_arr[index][0]
        anime_start = 0
        anime_end = 0
        if start_arr[index][2] == '':
            anime_start = int(start_arr[index][1][1])
        else:
            anime_start = int(start_arr[index][2])
        if end_arr[index][2] == '':
            anime_end = int(end_arr[index][1][1])
        else:
            anime_end = int(end_arr[index][2])

        novel_anime_premire_list.append({
            'volume_start': volume_start,
            'anime_start': anime_start,
            'volume_end': volume_end,
            'anime_end': anime_end,
        })

    novel_info.set_anime_start_and_end(novel_anime_premire_list)
    logging.info(f'MANGA_ANIME_START_AND_END = {novel_info.anime_start_and_end}')


# What if n/A
def set_novel_info_image_url(novel_info, soup):
    # title 처리
    try:
        img_url = soup.find('img')['src']
    except TypeError as e:
        img_url = ''
    novel_info.set_image_url(img_url)
    logging.info(f'URL = {novel_info.image_url}')

def set_novel_info_genre(novel_info, soup):
    genres = soup.get_text(separator='\n').strip().split('\n')
    genres = [item.strip() for item in genres if item.strip() and item.strip() != 'Search for series of same genre(s)']
    novel_info.set_genres(genres)
    logging.info(f'GENRES = {novel_info.genres}')


# What if N/A
def set_novel_info_authors(novel_info, soup):
    # authors = soup.get_text(separator='\n')
    authors = regex_delete_add(
        soup.get_text(separator='\n').strip()
    ).split('\n')
    if authors[0] == 'N/A':
        authors = []
    novel_info.set_authors(authors)
    logging.info(f'AUTHORS = {novel_info.authors}')

# What if N/A
def set_novel_info_artists(novel_info, soup):
    # title 처리
    artists = regex_delete_add(
        soup.get_text(separator='\n').strip()
    ).split('\n')
    if artists[0] == 'N/A':
        artists = []
    novel_info.set_artists(artists)
    logging.info(f'ARTISTS= {novel_info.artists}')

# What if N/A
def set_novel_info_year(novel_info, soup):
    # title 처리
    year = soup.get_text().strip()
    if year == 'N/A':
        year = ''
    novel_info.set_year(year)
    logging.info(f'YEAR={year}')

# What if N/A
def set_novel_info_original_publisher(novel_info, soup):
    publisher = regex_delete_add(
        soup.get_text(separator='\n').strip()
    ).split('\n')

    if publisher[0] == 'N/A':
        publisher = []
        logging.info(f'ORIGINAL_PUBLISHER= {novel_info.original_publisher}')
        novel_info.set_original_publisher(publisher)
        return

    original_publisher_list = []
    for i, pub in enumerate(publisher):
        # 지금 보고 있는게 (...) 라면 반복
        if re.compile(r'\(.*\)').search(pub) is not None:
            continue

        # 지금 보고 있는게 마지막 인덱스라면, label이 없으니 그냥 저장
        if i == (len(publisher) - 1):
            original_publisher_list.append({
                'publisher': pub.strip(),
                'label': ''
            })
        else:
            # 적어도 다음 index는 남아있다는 소리
            next_item = publisher[i+1]
            pattern = re.compile(r'\((?!Web Novel|Light Novel)(.*)\)')
            parenthesis = re.compile(r'\((.*)\)')
            # 그 다음 item이 괄호가 아님.
            if parenthesis.search(next_item) is None:
                original_publisher_list.append({
                    'publisher': pub.strip(),
                    'label': ''
                })
                continue
            # 그 다음 item이 괄호임 publisher (..label,..)
            else:
                # [Add]. Web Novel Light Novel이 아님. 즉, label임.
                if pattern.search(next_item):
                    label = parenthesis.search(next_item).group(1).strip()
                    original_publisher_list.append({
                        'publisher': pub.strip(),
                        'label': label.strip(),
                    })
                # 상기 이유임.
                else:
                    original_publisher_list.append({
                        'publisher': pub.strip(),
                        'label': ''
                    })
    novel_info.set_original_publisher(original_publisher_list)
    logging.info(f'ORIGINAL_PUBLISHER= {novel_info.original_publisher}')


# What if N/A
def set_novel_info_serialized_in(novel_info, soup):
    serialized_in = soup.get_text(separator='\n').strip().split('\n')
    serialized_in_arr = []
    if serialized_in[0] == 'N/A':
        serialized_in_arr = []
    else:
        for i in range(int(len(serialized_in) / 2)):
            label = serialized_in[2*i]
            publisher = serialized_in[2*i+1]
            pattern = re.compile(r'.*\((.*)\)')
            publisher = pattern.match(publisher).group(1)
            label_and_publisher = {
                'publisher': publisher.strip(),
                'label': label.strip()
            }
            serialized_in_arr.append(label_and_publisher)

    novel_info.set_serialized_in(serialized_in_arr)
    logging.info(f'SERIALIZED_IN= {novel_info.serialized_in}')


def regex_delete_add(string_):
    pattern = re.compile(r'\[\s*Add\s*\]|\xa0')
    string_ = pattern.sub("", string_)
    return string_


# get_practice_html()
# read_practice_html()   # FOR PRACTICING

# scrape_novel_info_thread_starter()

iterate_over_batch_files()
