import selenium.webdriver.firefox.options
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import ProxyType

from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def create_proxy_options(proxy_ip):
    options = {
        "http": proxy_ip,
        "https:": proxy_ip
    }
    return options

def createProxyWebDriver_ff(proxy, detatch=False):
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        'proxyType': 'manual',
        'httpProxy': proxy,
        'sslProxy': proxy,
    }
    ff_options=selenium.webdriver.firefox.options.Options()
    # chrome_options.add_experimental_option("detach", detach)
    # ff_options.add_argument("--headless=new")
    # chrome_options.add_argument('--proxy-server=http://%s' % proxy); print(f"--proxy-server={proxy}")
    ff_options.add_argument("--incognito")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
    ff_options.add_argument('user-agent=' + user_agent)

    return webdriver.Chrome(options=ff_options)




def createProxyWebDriver(proxy, detach=False):
    # proxy 설정
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": proxy,
        "sslProxy": proxy,
        "ftpProxy": proxy,
        "proxyType": "manual",
        "autodetect": False,
    }
    # headless browser 설정
    chrome_options = Options()

    chrome_options.add_experimental_option("detach", detach)
    # chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument('--proxy-server=http://%s' % proxy); print(f"--proxy-server={proxy}")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
    # chrome_options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    chrome_options.add_argument('user-agent=' + user_agent)

    return webdriver.Chrome(options=chrome_options)


def driver_proxy_test(proxy):
    driver = createProxyWebDriver(proxy, True)
    driver.get("https://myexternalip.com/")
    page= driver.page_source
    print(page)

def anidb_proxy_test(proxy):
    driver = createProxyWebDriver(proxy, True)
    driver.get("https://anidb.net/anime/5391")
    page = driver.page_source
    print(page)

def proxy_test(proxy, url):
    driver = createProxyWebDriver(proxy, True)
    driver.get(url)
    page = driver.page_source
    print(page)


def proxy_test_ff(proxy, url):
    driver = createProxyWebDriver_ff(proxy, True)
    driver.get(url)
    page = driver.page_source
    print(page)


# def seleniumbase_test(proxy):
#     driver = Driver(uc=True, proxy=proxy)
#     driver.get("https://anidb.net/anime/4317")


# driver_proxy_test("20.205.61.143:80")
# anidb_proxy_test("47.243.166.133:18080")
# proxy_test("47.243.166.133:18080", "https://anidb.net/anime/5391")
# proxy_test("160.86.242.23:8080", "https://anidb.net/anime/12142")
proxy_test("160.86.242.23:8080", "https://www.mangaupdates.com/")
# proxy_test_ff("3.10.93.50:80", "https://anidb.net/anime/5391")

"""
    0. 반복
        1. proxy 선택 -- Random / Sequential
        2. Driver 생성
        3. Driver 사용
        4. Dirver 폐기
"""

