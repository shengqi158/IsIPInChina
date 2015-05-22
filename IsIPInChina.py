#!env python
#coding=utf-8
# 
# Author:       
# 
# Created Time: Thu 21 May 2015 09:50:28 PM EDT
# 
# FileName:     filter_ip.py
# 
# Description:  
# 
# ChangeLog:
import urllib2
import re
import sets
import bs4
import optparse
import sys
import traceback

def get_ip_port(file_name):
    urls = sets.Set()
    ip_port_git_pattern = re.compile(r'(http://\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5})/+.git/config', re.I)
    with open(file_name,'r') as fd:
        for line in fd:
            line = line.strip()
            match_git = re.search(ip_port_git_pattern, line)
            if match_git :
                url = match_git.groups()[0]
                urls.add(url)


    return urls


def is_url_200(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent':user_agent}
    try:
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        if response and response.getcode() == 200:
            return True
        else:
            return False
    except Exception,e:
        print 'url wrong', url, e
        return False

def is_in_china(url):
    """<div id="result"><div class="well"><p>查询的 IP：<code>114.114.114.114</code> 来自：江苏省南京市 信风网络</p><p>GeoIP: Nanjing, Jiangsu, China</p><p>Abovenet Communications</p></div></div>"""

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
    referer = 'http://www.ip.cn/index.php?ip=http%3A%2F%2F203.179.55.190'
    headers = {'User-Agent':user_agent,'Referer':referer}
    url_search = 'http://www.ip.cn/index.php?ip=%s' %(url)
    try:
        req = urllib2.Request(url_search, headers = headers)
        response = urllib2.urlopen(req,timeout=30)
        if response and response.getcode() == 200:
            data = response.read()
            soup = bs4.BeautifulSoup(data)
            result = soup.find_all(id="result")
#            print 'result:',result
            if result:
                #search_obj = re.search(r'<p>GeoIP:(.*)</p>', result[0])
                #location = search_obj.groups()[0]
                location = result[0].select('p')[1].get_text()
                search_obj = re.search(r'GeoIP:(.*)', location)
                location_real = search_obj.groups()[0]
                if 'China' in location_real:
                    return (True, location_real)
        elif response.getcode != 200:
            print 'bei qiang pingbi le',url
        return (False, None)
    except Exception,e:
        print 'error in judge ip location',url,e
        traceback.print_exc()
        return (False, None)

def write_file(src, dst):
    ips = get_ip_port(src)
#    print 'ips',ips
    if ips:
        try:
            with open(dst, 'w') as fd:
                for url in ips:
                    print 'url', url
                    if is_url_200(url):
                        result = is_in_china(url)
                        print 'result:',result
                        if result[0]:
                            fd.write(url +":  " + result[1] + "\n")
        except Exception,e:
            print 'no permission',e

def main():

    parser = optparse.OptionParser()
    parser.add_option('-s', '--src', dest='src_file', help='要测试的url的文件')
    parser.add_option('-d', '--dst', dest='dst_file', help='要写入的文件', default='url_ok.txt')
    (options,args) = parser.parse_args()
    if not options.src_file:
        print 'python filter_ip.py -s src_file -d dst_file'
        sys.exit()
    write_file(options.src_file, options.dst_file)


if __name__ == "__main__":
    main()
