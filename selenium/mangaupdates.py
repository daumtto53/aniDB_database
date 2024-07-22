import random
import re
import time

from selenium import webdriver
import selenium.webdriver.chrome.options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from utils import utils
from queue import Queue

# PreProcess START
# PROXYDIR = "../resources/https/https_proxies_general.txt"
PROXYDIR = "../resources/https/https_proxies_0722.txt"
MAIN_PAGE = "https://www.mangaupdates.com/"

useragents = utils.get_useragents()
randomProxy = utils.get_proxies(PROXYDIR)
links = []
seriallized_id= []
# PreProcess END

def save_links_to_file(links) :
    with open("../resources/mangaupdates/novel_links.txt",'a') as f:
        for linkstr in links:
            f.write(linkstr)
            f.write('\n')

    pattern = re.compile(r'/series/([a-zA-Z0-9]+)/')
    with open("../resources/mangaupdates/novel_id", "a") as f:
        for linkstr in links:
            match = pattern.search(linkstr)
            f.write(match.group(1))
            f.write('\n')


"""
    Browser Options 설정 체크
    * referer
    * headless / detach
"""
def createProxyWebDriver_Chrome(proxy, testing = True):
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

    user_agent = useragents[int(random.uniform(0, len(useragents)-1))]
    chrome_options.add_argument('user-agent=' + user_agent)

    return webdriver.Chrome(options=chrome_options)


"""
    > driver_behavior
    1. access main page
    2. 
"""
def driver_test() :
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
    #Select By Page
    time.sleep(random.uniform(1,3))
    driver.implicitly_wait(10)
    select = Select(driver.find_element(By.NAME, "perpage"))
    select.select_by_visible_text('100')
    driver.find_element(By.XPATH, '//button[normalize-space()="Go"]').click()
    # driver.find_element(By.CLASS_NAME, "p-0 text").find_element(By.CLASS_NAME, "btn btn-primary inbox").click();

    ##### https://www.mangaupdates.com/series.html?page=1&type=novel&perpage=100&display=list 에 진입 ####
        ## 반복 시작
    # content 반환
    time.sleep(random.uniform(2,5))
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

def start_from_page(pageNum) :
    driver = createProxyWebDriver_Chrome(
        "172.183.241.1:8080"
        # "160.86.242.23:8080"
    )
    driver.get(f"https://www.mangaupdates.com/series.html?page={pageNum}&type=novel&perpage=100&display=list")
    time.sleep(random.uniform(2,5))
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




# driver_test()
start_from_page(35)
