import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rs = requests.session()


def over18(url):
    res = rs.get(url, verify=False)
    # 先檢查網址是否包含'over18'字串 ,如有則為18禁網站
    if 'over18' in res.url:
        print("18禁網頁")
        # 從網址獲得版名
        board = url.split('/')[-2]
        load = {
            'from': '/bbs/{}/index.html'.format(board),
            'yes': 'yes'
        }
        res = rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
    return BeautifulSoup(res.text, 'html.parser'), res.status_code


# 移除特殊字元（移除Windows上無法作為資料夾的字元）
def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c, '')
    return value.rstrip()


def image_url(link):
    # 符合圖片格式的網址
    image_seq = ['.jpg', '.png', '.gif', '.jpeg']
    for seq in image_seq:
        if link.endswith(seq):
            return link
    # 有些網址會沒有檔案格式， "https://imgur.com/xxx"
    if 'imgur' in link:
        return '{}.jpg'.format(link)
    return ''


def replace_to_https(url):
    if not url.startswith('https'):
        return url.replace('http', 'https')
    return url


def store_pic(url):
    # 檢查看板是否為18禁,有些看板為18禁
    soup, _ = over18(url)
    # 避免有些文章會被使用者自行刪除標題列
    pic_url_list = []

    # 抓取圖片URL(img tag )
    for img in soup.find_all("a", rel='nofollow'):
        img_url = image_url(img['href'])
        if img_url:
            pic_url_list.append(replace_to_https(img_url))

    return pic_url_list

def store_comment(url):
    soup, _ = over18(url)
    comments_list = []

    for tag in soup.select('div.push'):
        comment = {}
        push_tag = tag.find("span", {'class': 'push-tag'}).text
        #print "push_tag:",push_tag
        push_userid = tag.find("span", {'class': 'push-userid'}).text       
        #print "push_userid:",push_userid
        push_content = tag.find("span", {'class': 'push-content'}).text   
        comment['content'] = push_content[1:]
        
	#print "push_content:",push_content
        #push_ipdatetime = tag.find("span", {'class': 'push-ipdatetime'}).text   
        #push_ipdatetime = remove(push_ipdatetime, '\n')
        #print "push-ipdatetime:",push_ipdatetime 
                
        #message[num]={"狀態":push_tag.encode('utf-8'),"留言者":push_userid.encode('utf-8'),
        #    "留言內容":push_content.encode('utf-8'),"留言時間":push_ipdatetime.encode('utf-8')}
        
        if push_tag == u'推 ':
            comment['rate'] = 1
        elif push_tag == u'噓 ':
            comment['rate'] = -1
        else:
            comment['rate'] = 0

        comments_list.append(comment)

    return comments_list
