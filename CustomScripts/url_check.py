import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

def check_url_status(url, timeout = 5):
    if not (url.startswith("http://") or url.startswith("https://")):
        #print("Error: URL should start with 'http://' or 'https://'")
        print(1)
        return
    try:
        response = urlopen(url, timeout = timeout)
        if response.status == 200:
            print(0)
        else:
            print(1)
    except HTTPError as e:
        print(1)
    except URLError as e:
        print(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    check_url_status(url)
