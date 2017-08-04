import time, os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
import schedule
import post_parser
from dbModel import Images, Articles, Comments, DB_connect

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rs = requests.session()

def get_page_number(content):
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1


def over18(board):
    res = rs.get('https://www.ptt.cc/bbs/{}/index.html'.format(board), verify=False)
    # 先檢查網址是否包含'over18'字串 ,如有則為18禁網站
    if 'over18' in res.url:
        print("18禁網頁")
        load = {
            'from': '/bbs/{}/index.html'.format(board),
            'yes': 'yes'
        }
        res = rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
    return BeautifulSoup(res.text, 'html.parser')


def craw_page(res, push_rate):
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                author  = r_ent.find(class_="author").text.strip()
                post_date = r_ent.find(class_="date").text.strip()
                title = r_ent.find(class_="title").text.strip()
                rate_text = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate_text:
                    if rate_text.startswith('爆'):
                        rate = 100
                    elif rate_text.startswith('X'):
                        rate = -10 * int(rate_text[1])
                    else:
                        rate = rate_text
                else:
                    rate = 0
                # 比對推文數
                if int(rate) >= push_rate:
                    article_seq.append({
                        'post_date': post_date,
                        'author': author,
                        'title': title,
                        'url': url,
                        'rate': rate,
                    })
        except Exception as e:
            print('本文已被刪除', e)
    return article_seq

def write_db_article(board, article_list, session):
    for article in article_list:
        is_exist = session.query(Articles).filter(Articles.url == article['url']).first()
        if not is_exist:
            data = Articles(board=board, author=article['author'],
                    title=article['title'], url=article['url'], rate=article['rate'])
            session.add(data)
    session.commit()

def update_db_article(article, session):
    is_exist = session.query(Articles).filter(Articles.url == article['url'],
                                              Articles.post_date == None).first()
    if is_exist:
        session.query(Articles).filter(Articles.url == article['url']).\
                update({Articles.post_date : article['post_date']})
        session.commit()

def write_db_comment(comments, article_url, session):
    is_exist = session.query(Comments).filter(Comments.url == article_url).first()
    if not is_exist:
        for comment in comments:
            data = Comments(url=article_url, commenter = comment['commenter'], 
                    comment_date = comment['comment_date'],
                    rate = comment['rate'], content=comment['content'])
            session.add(data)
        session.commit()

def write_db(images, article_url, session):
    for image in images:
        is_exist = session.query(Images).filter(Images.url == image).first()
        if not is_exist:
            data = Images(url=article_url, imgurl=image)
            session.add(data)
    session.commit()


def connect_db(db_string):
    engine = create_engine(db_string)
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return engine, session


def main(board='beauty', crawler_pages=2):
    engine, session = connect_db(DB_connect)
    # python beauty_spider2.py [版名]  [爬幾頁] [推文多少以上]
    page_term, push_rate = crawler_pages, -100
    start_time = time.time()
    soup = over18(board)
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page = get_page_number(all_page_url)

    print("Analytical download page...")
    index_list = []
    article_list = []
    for page in range(start_page, start_page - page_term, -1):
        page_url = 'https://www.ptt.cc/bbs/{}/index{}.html'.format(board, page)
        index_list.append(page_url)

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)
        res = rs.get(index, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            index_list.append(index)
            time.sleep(1)
        else:
            article_list += craw_page(res, push_rate)
        time.sleep(0.05)

    total = len(article_list)
    print(article_list)
    write_db_article(board, article_list, session)
    count = 0
    image_seq = []
    # 進入每篇文章分析內容
    while article_list:
        article = article_list.pop(0)
        article_url = article['url']
        res = rs.get(article_url, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            article_list.append(article)
            time.sleep(1)
        else:
            is_exist = session.query(Articles).filter(Articles.url == article_url)
            if is_exist:
                article_content = post_parser.store_article(article_url, article)
                update_db_article(article_content, session)
                count += 1
                # 儲存圖面
                image_seq += post_parser.store_pic(article_url)
                write_db(image_seq, article_url, session)

                # 儲存推文
                comments_list = post_parser.store_comment(article)
                #print(comments_list)
                write_db_comment(comments_list, article_url, session)

                print('download: {:.2%}'.format(count / total))
        time.sleep(0.05)

    # disconnect
    session.close()
    engine.dispose()

    print("下載完畢...")
    print('execution time: {:.3}s'.format(time.time() - start_time))


if __name__ == '__main__':
    board = os.environ['PTT_BOARD']
    pages = int(os.environ['PTT_PAGES'])
    crawler_interval = int(os.environ['PTT_CRAWLER_INTERVAL'])
    print('main')
    main(board, pages)
    schedule.every(crawler_interval).minutes.do(main)
    while True:
        print('wating......')
        schedule.run_pending()
        time.sleep(10)
