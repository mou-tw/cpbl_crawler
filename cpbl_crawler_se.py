from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re

options = Options()
options.add_argument("--disable-notifications")

def parse_hitter_page(page):
    chrome = webdriver.Chrome('./chromedriver', options=options)
    chrome.get("https://www.cpbl.com.tw/stats/recordall")
    print('start')
    # soup = BeautifulSoup(chrome.page_source, 'html.parser')
# player = chrome.find_element_by_xpath("//a[@target='_blank']")
# print(player)

# soup = BeautifulSoup(chrome.page_source, 'html.parser')
# print(len(soup.find_all(href=re.compile("person"))))
# for i in soup.find_all(href=re.compile("person")):
#     print('https://www.cpbl.com.tw' + i['href'])

# soup.select('article[class="b-block--top-bord job-list-item b-clearfix js-job-item"]')

    for i in range(page):
        p = i+1
        if i % 10 == 0 and i!=0:
            print('do a')
            print(f"""//a[@title='第 {p} 頁']""")
            chrome.find_element_by_xpath(f"""//a[@title='下一頁']""").click()
            print('done click')
            time.sleep(0.7)
            # print(f"//a[@title='第 {i+1} 頁']")
            # print(f"//a[@title='第 {i + 2} 頁']")
            # chrome.get("https://www.cpbl.com.tw/stats/recordall")
            soup = BeautifulSoup(chrome.page_source, 'html.parser')
            print(len(soup.find_all(href=re.compile("person"))))
            for ii in soup.find_all(href=re.compile("person")):
                with open('../doc_file/url_lst.txt', 'a') as f:
                    r = 'https://www.cpbl.com.tw' + ii['href'] + '\n'
                    f.write(r)
                print('https://www.cpbl.com.tw' + ii['href'])

            time.sleep(0.7)

        else:
            print('do b')
            print(f"""//a[@title='第 {p} 頁']""")
            chrome.find_element_by_xpath(f"""//a[@title='第 {p} 頁']""").click()
            print('done click')
            time.sleep(0.7)
            # print(f"//a[@title='第 {i+1} 頁']")
            # print(f"//a[@title='第 {i + 2} 頁']")
            # chrome.get("https://www.cpbl.com.tw/stats/recordall")
            soup = BeautifulSoup(chrome.page_source, 'html.parser')
            print(len(soup.find_all(href=re.compile("person"))))
            for ii in soup.find_all(href=re.compile("person")):
                with open('../doc_file/url_lst.txt', 'a') as f:
                    r = 'https://www.cpbl.com.tw' + ii['href'] +'\n'
                    f.write(r)
                print('https://www.cpbl.com.tw' + ii['href'])

            time.sleep(0.7)


    chrome.close()

if __name__ == '__main__':
    st= time.time()
    parse_hitter_page(56)
    print (f' time cost :{time.time()-st} sec')