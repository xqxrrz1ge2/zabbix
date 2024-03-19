import sys
import urllib2

def check_url_status(url):
    try:
        response = urllib2.urlopen(url)
        # 如果状态码是200，打印0；否则打印1
        if response.getcode() == 200:
            print 0
        else:
            print 1
    except urllib2.HTTPError as e:
        # 如果服务器能够对请求作出响应，但是响应的是一个错误代码，打印1
        print 1
    except urllib2.URLError as e:
        # 如果我们无法达到服务器（比如URL错误，或网络问题），打印1
        print 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python script.py <url>"
        sys.exit(1)
    url = sys.argv[1]
    check_url_status(url)
