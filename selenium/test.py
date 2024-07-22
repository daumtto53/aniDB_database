from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import traceback



def createProxyWebDriver(proxy, detach=False):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", detach)
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("ignore-certificate-errors")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')

    # Use ChromeDriverManager to get the appropriate driver
    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)

def proxy_test(proxy, url):
    try:
        driver = createProxyWebDriver(proxy, True)
        print(f"Attempting to access {url} using proxy {proxy}")

        driver.get(url)

        # Wait for the body to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        print("Page loaded successfully")
        print("Page title:", driver.title)

        # Get and print the current URL (in case of redirects)
        current_url = driver.current_url
        print("Current URL:", current_url)

        # Try to find and print an element that should be on the page
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            print("Found h1 element:", element.text)
        except:
            print("Couldn't find h1 element")

        # Save page source to a file for inspection
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to 'page_source.html'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
    finally:
        if 'driver' in locals():
            driver.quit()

# Test with a reliable site first, then try your target site
proxy_test("80.249.112.162:80", "https://the-internet.herokuapp.com/?ref=hackernoon.com")
