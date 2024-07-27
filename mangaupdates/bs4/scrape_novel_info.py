import re

import requests
import utils.utils
import os.path

import logging
import sys

from bs4 import BeautifulSoup
from langdetect import detect

from mangaupdates.NovelInfo import NovelInfo


# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scrape_novel_info.log", mode="w", encoding='utf-8'),
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

def get_practice_html():
    headers = utils.utils.get_headers(useragent)
    proxy = utils.utils.get_randomzied_element(proxies)
    link = "https://www.mangaupdates.com/series/3qzxncc/re-zero-kara-hajimeru-isekai-seikatsu-novel"
    novel_info_request = requests.get(
        link,
        proxies={'http': proxy},
        headers=headers
    )
    try:
        soup = BeautifulSoup(novel_info_request.text, 'html.parser').find('body')
        with open("../../practice/rezero.html", 'w', encoding='utf-8') as f:
            f.write(novel_info_request.text)
    except Exception as e:
        print(e)


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
    # link = "https://www.mangaupdates.com/series/qo1rsw8/mondaiji-tachi-ga-isekai-kara-kuru-sou-desu-yo-novel"
    # link = "https://www.mangaupdates.com/series/261v4f9/ark-novel"
    # link = "https://www.mangaupdates.com/series/kx3b4pm/bungaku-shoujo-novel"
    # link = "https://www.mangaupdates.com/series/yuu8te1/the-sketch-artist-novel"
    # link = "https://www.mangaupdates.com/series/zzzieh2/that-one-time-the-essay-a-child-wrote-over-summer-break-was-way-too-fantasy-novel"
    # link = "https://www.mangaupdates.com/series/yuu8te1/the-sketch-artist-novel"
    # link = "https://www.mangaupdates.com/series/yo6kq0f/i-bought-the-crown-prince-because-he-was-being-sold-at-the-slave-market-novel"

    # link = "https://www.mangaupdates.com/series/ouam6mt/zero-no-tsukaima-novel"
    # link = "https://www.mangaupdates.com/series/be9td6r/madan-no-ou-to-senki-novel"
    # link = "https://www.mangaupdates.com/series/rullw8t/saenai-kanojo-no-sodatekata-novel"
    # link = "https://www.mangaupdates.com/series/z4ycn3t/shinigami-no-ballad-novel"
    link = "https://www.mangaupdates.com/series/ouam6mt/zero-no-tsukaima-novel"
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
    # set_novel_info_anime_start_end(novel_info, to_parse_list[8])
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
    logging.info(f"title={novel_info.title}")

def set_novel_info_description(novel_info, soup):
    desc = ''
    if soup.find("div", {"id": "div_desc_more"}):
        desc = soup.find("div", {"id": "div_desc_more"}).get_text().strip()
    else:
        desc = soup.get_text().strip()
    novel_info.set_description(desc)
    logging.info(f"desc={novel_info.description}")

def set_novel_info_type(novel_info, soup):
    novel_info.set_type(soup.get_text().strip())
    logging.info(f"type={novel_info.type}")

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
    logging.info(f'related_series = {related_series_list}')


def set_novel_info_associated_names(novel_info, soup):
    associated_names_list = []
    associated_names_list.append({
        'title': novel_info.title,
        'language': 'en'
    })
    associated_names = [text.strip() for text in soup.stripped_strings]
    for e in associated_names:
        e = e.strip()
        pattern = re.compile(r'^(.*?)(?:\s*(\(.*\)))?$')
        match = pattern.match(e)

        associated_name = match.group(1).strip()
        if (associated_name is not None):
            language_detected = detect(associated_name)
            logging.info(f'associated_name = {associated_name}, language={language_detected}')

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
    logging.info(f"associated_names={novel_info.associated_names} [[ title = {novel_info.title} ]]")


def set_novel_info_status_in_origin_country(novel_info, soup):
    volume = 0
    status = ''

    text_content = soup.get_text(separator='\n').strip()
    pattern = re.compile(r'(?:(\d+)\s*)Volumes?\s*\((.*)\)|(Oneshot)\s*\((.*)\)')
    matches = pattern.findall(text_content)

    for match in matches:
        logging.info(f"match={match}")
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
    logging.info(f'status_in_original_country={novel_info.status_in_origin_country}')


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

    Vol\s*(\d+)(?:.*?)?(?:\(S(\d+).*?\)|\((.*)\))? vs N/A
    
"""
# def set_novel_info_anime_start_end(novel_info, soup):
#     novel_anime_premire_list = []
#     print(soup.get_text())
#     if soup.get_text() == 'N/A':
#         set_novel_info_anime_start_end([])
#         return
#     text_content = soup.get_text(separator='\n')
#     logging.info(f'text_content={text_content}')
#
#     #Starts\s*at\s*(?:(?:Vol\s*(\d+)\s*(?:\((S\d+|.*)\))?))*(?:.*[\r\n]*)(?:Ends\s*at\s*(?:(?:Vol\s*(\d+)\s*(?:\((S\d+|.*)\))?))*)?
#     pattern = re.compile(r'(?:Vol\s*(\d+)\s*(?:\((S\d+|.*)\))?)')
#     matches = pattern.findall(text_content[0])
#     print(matches)


    # novel_info.set_title(title)
    # print(novel_info.title)

def set_novel_info_image_url(novel_info, soup):
    # title 처리
    img_url = soup.find('img')['src']
    novel_info.set_image_url(img_url)
    logging.info(novel_info.image_url)

def set_novel_info_genre(novel_info, soup):
    # title 처리
    genres = soup.get_text(separator='\n').strip().split('\n')
    genres = [item.strip() for item in genres if item.strip() and item.strip() != 'Search for series of same genre(s)']
    novel_info.set_genres(genres)
    logging.info(f'GENRES = {novel_info.genres}')


def set_novel_info_authors(novel_info, soup):
    authors = soup.get_text(separator='\n').strip().split('\n')
    novel_info.set_authors(authors)
    logging.info(f'authors = {novel_info.authors}')

def set_novel_info_artists(novel_info, soup):
    # title 처리
    artists = soup.get_text(separator='\n').strip().split('\n')
    novel_info.set_artists(artists)
    logging.info(f'artists= {novel_info.artists}')

def set_novel_info_year(novel_info, soup):
    # title 처리
    year = soup.get_text().strip()
    novel_info.set_year(year)
    logging.info(f'year={year}')

def set_novel_info_original_publisher(novel_info, soup):
    publisher = soup.get_text(separator='\n').strip().split('\n')
    if publisher[0] == 'N/A':
        publisher = []
    novel_info.set_original_publisher(publisher)
    logging.info(f'original_publisher= {novel_info.original_publisher}')


def set_novel_info_serialized_in(novel_info, soup):
    serialized_in = soup.get_text(separator='\n').strip().split('\n')
    if serialized_in[0] == 'N/A':
        serialized_in = []
    novel_info.set_artists(serialized_in)
    logging.info(f'serialized_in= {novel_info.serialized_in}')

# def set_novel_info_(novel_info, soup):
#     # title 처리
#     title = soup.find("span", {"class": "releasestitle tabletitle"}).get_text()
#     novel_info.set_title(title)
#     print(novel_info.title)
#
#
# def set_novel_info_(novel_info, soup):
#     # title 처리
#     title = soup.find("span", {"class": "releasestitle tabletitle"}).get_text()
#     novel_info.set_title(title)
#     print(novel_info.title)
#
#
# def set_novel_info_(novel_info, soup):
#     # title 처리
#     title = soup.find("span", {"class": "releasestitle tabletitle"}).get_text()
#     novel_info.set_title(title)
#     print(novel_info.title)
#
# def set_novel_info_(novel_info, soup):
#     # title 처리
#     title = soup.find("span", {"class": "releasestitle tabletitle"}).get_text()
#     novel_info.set_title(title)
#     print(novel_info.title)

# get_practice_html()
read_practice_html()
