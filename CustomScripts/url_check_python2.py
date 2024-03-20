import sys
import urllib2

def check_url_status(url, timeout = 10):
    if not (url.startswith("http://") or url.startswith("https://")):
        print "Error: URL should start with 'http://' or 'https://'"
        return
    
    try:
        response = urllib2.urlopen(url, timeout = timeout)
        if response.getcode() == 200:
            print 0
        else:
            print 1
    except urllib2.HTTPError as e:
        print 1
    except urllib2.URLError as e:
        print 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python script.py <url>"
        sys.exit(1)
    url = sys.argv[1]
    check_url_status(url)
