import requests

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def createProxies(ip) :
    return {
        "http": ip,
        # "https": ip
    }

if __name__ == '__main__':
    print_hi('PyCharm')

    res = requests.get("https://www.mangaupdates.com/series.html?type=novel&orderby=rating&display=list&perpage=100",
                       proxies=createProxies("45.124.87.33:3128"), timeout=20)
    print(res.status_code)
    print(res)
    print(res.content)



