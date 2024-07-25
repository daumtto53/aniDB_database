import random
import re
import time
import logging
import sys

import requests
from selenium import webdriver
import selenium.webdriver.chrome.options
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from lxml import etree

from utils import utils
from queue import Queue

# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scrape_novel_links_last.log", mode="w"),
    ],
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# PreProcess START
# PROXYDIR = "../resources/https/https_proxies_general.txt"
PROXYDIR = "../resources/https/https_proxies_0722.txt"
MAIN_PAGE = "https://www.mangaupdates.com/"

useragents = utils.get_useragents()
randomProxy = utils.get_https_proxies()
seriallized_id = []



# PreProcess END

def selenium_test():
    driver = createProxyWebDriver_Chrome(
        "172.183.241.1:8080"
        # "160.86.242.23:8080"
    )
    driver.get(f"https://www.mangaupdates.com/series.html?page=12&type=novel&perpage=100&display=list")
    time.sleep(random.uniform(2, 5))


def save_links_to_file(links, filedir1, filedir2, pattern_input):
    with open(filedir1, 'a') as f:
        for linkstr in links:
            f.write(linkstr)
            f.write('\n')

    pattern = re.compile(pattern_input)
    with open(filedir2, "a") as f:
        for linkstr in links:
            match = pattern.search(linkstr)
            f.write(match.group(1))
            f.write('\n')


def save_only_links_to_file(links, filedir1):
    with open(filedir1, 'a') as f:
        for linkstr in links:
            f.write(linkstr)
            f.write('\n')



"""
    Browser Options 설정 체크
    * referer
    * headless / detach
"""


def createProxyWebDriver_Chrome(proxy, testing=True):
    # proxy 설정
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": proxy,
        "sslProxy": proxy,
        "ftpProxy": proxy,
        "proxyType": "manual",
        "autodetect": False,
    }
    # headless browser 설정
    chrome_options = selenium.webdriver.chrome.options.Options()

    if testing == True:
        chrome_options.add_experimental_option("detach", True)
        # chrome_options.add_argument("--headless=new") # SHOULD NOT USEIT WITH DETACH
        # chrome_options.add_argument('--proxy-server=http://%s' % proxy); print(f"--proxy-server={proxy}")
        # chrome_options.add_argument("--incognito")
        chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
        chrome_options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함
    else:
        # chrome_options.add_argument('--proxy-server=http://%s' % proxy); print(f"--proxy-server={proxy}")
        # chrome_options.add_experimental_option("detach", detach)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
        chrome_options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함

    user_agent = useragents[int(random.uniform(0, len(useragents) - 1))]
    chrome_options.add_argument('user-agent=' + user_agent)

    return webdriver.Chrome(options=chrome_options)


"""
    > driver_behavior
    1. access main page
    2. 
"""


def driver_test():
    # driver = createProxyWebDriver_Chrome(
    #     randomProxy[int(random.uniform(0, len(randomProxy) - 1))]
    # )
    driver = createProxyWebDriver_Chrome(
        "172.183.241.1:8080"
        # "160.86.242.23:8080"
    )
    driver.get(MAIN_PAGE)
    # driver.execute_script("location.reload()")
    driver.implicitly_wait(10)
    time.sleep(1)
    # Proxy가 안먹히는 경우 -- 외부 반복 / Continue
    # driver.find_element(By.CLASS_NAME, "p-1 text text-center side_dark_content_row right_search_row")
    driver.find_element(By.LINK_TEXT, "Advanced Search").click()
    # wait until load
    driver.implicitly_wait(10)

    # advanced_search for novel

    # 잘 안될떄 뒤로갔다가 앞으로 오기
    driver.back()
    time.sleep(2)
    driver.forward()

    time.sleep(1)
    driver.find_element(By.ID, "type-option-caee3e9d54b49ae50aa4ae7bbe306decdf2028aa").click()
    driver.find_element(By.ID, "display-option-38b62be4bddaa5661c7d6b8e36e28159314df5c7").click()
    driver.find_element(By.CLASS_NAME, "button").click()
    # Select By Page
    time.sleep(random.uniform(1, 3))
    driver.implicitly_wait(10)
    select = Select(driver.find_element(By.NAME, "perpage"))
    select.select_by_visible_text('100')
    driver.find_element(By.XPATH, '//button[normalize-space()="Go"]').click()
    # driver.find_element(By.CLASS_NAME, "p-0 text").find_element(By.CLASS_NAME, "btn btn-primary inbox").click();

    ##### https://www.mangaupdates.com/series.html?page=1&type=novel&perpage=100&display=list 에 진입 ####
    ## 반복 시작
    # content 반환
    time.sleep(random.uniform(2, 5))
    next_button_exists = True
    while next_button_exists:
        content = driver.page_source
        # bs4 사용
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for ele in soup.select('div[class*="col-6 py-1 py-md-0"]'):
            links.append(ele.find('a').get('href'))
        save_links_to_file(links)
        links.clear()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Next Page"))).click()
        time.sleep(2)
        print(driver.current_url)
        driver.implicitly_wait(4)
        next_button_exists = driver.find_element(By.LINK_TEXT, "Next Page").is_displayed()
        time.sleep(random.uniform(3, 8))

    print("all_clear")



def start_from_page(pageNum):
    driver = createProxyWebDriver_Chrome(
        "172.183.241.1:8080"
        # "160.86.242.23:8080"
    )
    driver.get(f"https://www.mangaupdates.com/series.html?page={pageNum}&type=novel&perpage=100&display=lis")
    time.sleep(random.uniform(2, 5))
    next_button_exists = True
    while next_button_exists:
        content = driver.page_source
        # bs4 사용
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for ele in soup.select('div[class*="col-6 py-1 py-md-0"]'):
            links.append(ele.find('a').get('href'))
        save_links_to_file(links)
        links.clear()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Next Page"))).click()
        time.sleep(2)
        print(driver.current_url)
        driver.implicitly_wait(4)
        next_button_exists = driver.find_element(By.LINK_TEXT, "Next Page").is_displayed()
        time.sleep(random.uniform(3, 8))


def get_publishers_list():
    # driver = createProxyWebDriver_Chrome(
    #     randomProxy[int(random.uniform(0, len(randomProxy) - 1))]
    # )
    driver = createProxyWebDriver_Chrome(
        "35.185.196.38:3128"
        # "160.86.242.23:8080"
    )
    driver.get(MAIN_PAGE)
    # driver.execute_script("location.reload()")
    driver.implicitly_wait(10)
    time.sleep(1)
    # Proxy가 안먹히는 경우 -- 외부 반복 / Continue
    # driver.find_element(By.CLASS_NAME, "p-1 text text-center side_dark_content_row right_search_row")
    driver.find_element(By.LINK_TEXT, "Publishers").click()
    # wait until load

    # Page 제한을 100개로 늘리기
    driver.implicitly_wait(10)
        # Select By Page
    time.sleep(random.uniform(1, 3))
    driver.implicitly_wait(10)
    select = Select(driver.find_element(By.NAME, "perpage"))
    select.select_by_visible_text('100')
    driver.find_element(By.XPATH, '//button[normalize-space()="Go"]').click()

    ##### https://www.mangaupdates.com/publishers.html 에 진입 ####
    ## 반복 시작
    # content 반환
    time.sleep(random.uniform(2, 5))
    next_button_exists = True
    while next_button_exists:
        content = driver.page_source
        # bs4 사용
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for ele in soup.select('div[class*="col-sm-6 p-1 p-md-0 col-8 text"]'):
            links.append(ele.find('a').get('href'))
        save_links_to_file(
            links,
            "../../resources/mangaupdates/publisher_links.txt",
            "../../resources/mangaupdates/publisher_id.txt",
            r'/publisher/([0-9a-zA-Z]+)/'
        )
        links.clear()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Next Page"))).click()
        time.sleep(2)
        print(driver.current_url)
        driver.implicitly_wait(4)
        next_button_exists = driver.find_element(By.LINK_TEXT, "Next Page").is_displayed()
        time.sleep(random.uniform(3, 8))

    print("all_clear")



# novel 긁어오기
# https://www.mangaupdates.com/series.html?type=novel&exclude_genre=Shounen+Ai_Yaoi&display=list&perpage=100
def get_novel_list():
    # driver = createProxyWebDriver_Chrome(
    #     randomProxy[int(random.uniform(0, len(randomProxy) - 1))]
    # )
    driver = createProxyWebDriver_Chrome(
        "35.185.196.38:3128"
        # "160.86.242.23:8080"
    )
    driver.get(MAIN_PAGE)
    # driver.execute_script("location.reload()")
    driver.implicitly_wait(10)

    # AdvancedSearch 진입
    driver.find_element(By.LINK_TEXT, "Advanced Search").click()
    # wait until load
    driver.implicitly_wait(10)
    # 잘 안될떄 뒤로갔다가 앞으로 오기
    driver.back()
    time.sleep(2)
    driver.forward()

    time.sleep(1)
    driver.find_element(By.ID, "gn23").click()  # Shonen AI DISALBE
    driver.find_element(By.ID, "gn15").click()  #Yaoi Disable

    driver.find_element(By.ID, "type-option-caee3e9d54b49ae50aa4ae7bbe306decdf2028aa").click()  #Select Novel
    driver.find_element(By.ID, "display-option-38b62be4bddaa5661c7d6b8e36e28159314df5c7").click() #SELECT LIST
    driver.find_element(By.CLASS_NAME, "button").click()

    time.sleep(1)
    # Proxy가 안먹히는 경우 -- 외부 반복 / Continue
    # driver.find_element(By.CLASS_NAME, "p-1 text text-center side_dark_content_row right_search_row")
    # wait until load

    # Page 제한을 100개로 늘리기
    driver.implicitly_wait(10)
        # Select By Page
    time.sleep(random.uniform(1, 3))
    driver.implicitly_wait(10)
    select = Select(driver.find_element(By.NAME, "perpage"))
    select.select_by_visible_text('100')
    driver.find_element(By.XPATH, '//button[normalize-space()="Go"]').click()

    ##### https://www.mangaupdates.com/publishers.html 에 진입 ####
    ## 반복 시작
    # content 반환
    time.sleep(random.uniform(2, 5))
    next_button_exists = True
    links = []
    while next_button_exists:
        logging.info(f"current_link={driver.current_url}, links={len(links)}")
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        for ele in soup.select('div[class*="col-6 py-1 py-md-0 text"]'):
            links.append(ele.find('a').get('href'))

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Next Page"))).click()
        time.sleep(2)
        driver.implicitly_wait(4)
        try:
            next_button_exists = driver.find_element(By.LINK_TEXT, "Next Page").is_displayed()
        except NoSuchElementException as e:
            logging.warning(f"NO_SUCH_ELEMENT_EXCEPTION, ERROR={e}")
            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            for ele in soup.select('div[class*="col-6 py-1 py-md-0 text"]'):
                links.append(ele.find('a').get('href'))
            # SAVE IT TO FILE
            logging.info(f"SAVING TO FILE....LINKS={links}")
            save_only_links_to_file(
                links,
                "../../resources/mangaupdates/novel_links.txt",
            )
            logging.info(f"SAVING TO FILE....COMPLETED! LINKS={links}")
        time.sleep(random.uniform(3, 15))

        print("all_clear")


def get_novel_list_last_page():
    driver = createProxyWebDriver_Chrome(
        "35.185.196.38:3128"
    )
    driver.get("https://www.mangaupdates.com/series.html?page=32&type=novel&perpage=100&exclude_genre=Shounen+Ai_Yaoi&display=list")
    driver.implicitly_wait(10)

    links = []
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    for ele in soup.select('div[class*="col-6 py-1 py-md-0 text"]'):
        links.append(ele.find('a').get('href'))
    # SAVE IT TO FILE
    logging.info(f"SAVING TO FILE....LINKS={links}")
    save_only_links_to_file(
        links,
        "../../resources/mangaupdates/novel_links_last_page.txt",
    )
    logging.info(f"SAVING TO FILE....COMPLETED! LINKS={links}")
    time.sleep(random.uniform(3, 15))

    print("all_clear")



"""
    requests 설정
    * user-agents
    * referer-
"""


def configure_header():
    # UserAgent는 똑같아야함.
    useragent = useragents[int(random.uniform(0, len(useragents) - 1))]
    referer = "https://www.mangaupdates.com/series.html?act=genresearch"
    headers = {
        'referer': referer,
        'useragent': useragent
    }
    return headers


def configure_proxy(ip) :
    return {
        # "http": "172.183.241.1:8080",
        "https": "172.183.241.1:8080",
        # "http": ip,
        # "https": ip
    }


# Proxy가 내부적으로 설정되어있는 상태.
def read_single_novel_info_page(url, proxy):
    try:
        # request 설정
        res = requests.get(url,
                           proxies=configure_proxy(proxy),
                           headers=configure_header(),
                           timeout=20
                           )
        # request에 대해서 HTML을 받아온다.
        if res.status_code == 200:
            # BeautifulSoup(content, 'html.parser')
            soup = BeautifulSoup(res.text, 'html.parser')
            # parse_all_novel_info(soup)
            print(soup.text)

        else:
            print(f"failed with status code: {res.status_code}")
    except requests.exceptions.Timeout as ex:
        print(f"WARNING: request timed out, STATUSCODE = {ex.response.status_code}")
    except requests.exceptions.RequestException as ex:
        print(f"WARNING: SOMETHING WRONG, STATUSCODE = {ex.response.status_code}")


"""
    parsing 해야 되는 정보
        * description
        * Type
        * Related Series-- 연관 시리즈
            * 배열
            * 제목 / 관계(스핀오프)
        * Associated Names -- 다른 언어 / 배열 / 
            * 배열
            * 제목 / (관계)
        * Status in Country of Origin -- 원작 발매 / 
            * 제목 (관계)
        * anime start / end chapter -- 애니 시작, 끝
            * 시작 / 시작 / 시작 ... 
            * 끝 / 끝 / 끝
        * Genre -- 장르
        * Authors -- 
            * 배열
            * 이름 (한자)
        * Artists
            * 배열
            * 이름 (한자)
        * Year
        * Original Publisher
            * 이름 (별칭)
        * Serialized in 
            * N/A || ?
            
        * 정발 유무
            * 
        * 애니화 유무
            * Anime Start / End Chapter
        * User Rating 
        * User Comments
"""


# read_single_novel_info_page("https://www.mangaupdates.com/series.html?id=6685", "172.183.241.1:8080")
# parse_all_novel_info(1)

# get_publishers_list()

# get_novel_list()
get_novel_list_last_page()
