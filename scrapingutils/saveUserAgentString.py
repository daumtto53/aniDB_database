import requests
from bs4 import BeautifulSoup

userAgents = []

try:
    req = requests.get("https://www.useragentstring.com/pages/Chrome/", timeout=5)
except requests.exceptions.Timeout as e:
    print(e)

html = BeautifulSoup(req.text, 'html.parser')
print(html)

uls = html.findAll('ul')

for e in uls:
    lis = e.find_all_next('li')
    for li in lis:
        userAgents.append(li.get_text())

print(userAgents)

with open("../resources/useragent/useragent.txt", "w+") as f :
    for agent in userAgents:
        f.write(agent)
        f.write("\n")

