import time
import random
from journals.common import Row_Name,common_website,common_journals,common_article
import requests
from bs4 import BeautifulSoup
import re
import json

def wait():
    time.sleep(random.random() * 4+3)

class journals(common_journals):

    def get(self,website,journal,url):
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER] = website
        wait()
        data = requests.get(url)
        # bs = BeautifulSoup(data.text, "html.parser")

        # div = bs.find("div", id="text2")
        # div1 = div.find("div", class_="wpmd")
        # print(div1)
        # for div_tag in div1.find_all("div"):
        #     if "Vol" in div_tag.get_text():
        #         year = None
        #         for font in div_tag.find_all("font"):
        #             f_line = font.get_text()
        #             year_f = re.search("\d{4}", f_line)
        #             if year_f != None:
        #                 year = year_f.group()
        #             if "Vol" in f_line:
        #                 a = font.find("a")
        #                 if a != None:
        #                     strings = f_line.split(",")
        #                     vol = strings[0].replace("Vol", "").strip()
        #                     issue = strings[1].replace("Issue", "").strip()
        #                     n_url = "http://bipublication.com/" + a['href']
        #                     issue_info = dict(journal_common_info)
        #                     issue_info[Row_Name.YEAR] = year
        #                     issue_info[Row_Name.VOLUME] = vol
        #                     issue_info[Row_Name.ISSUE] = issue
        #                     issue_info[Row_Name.TEMP_URL]=n_url
        #
        #                 if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
        #                     self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1481-8043",Row_Name.EISSN:"1481-8035"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", id="table1")
        # print(div)
        table = div.find("table")
        for tr in table.find_all("tr"):
            info=dict(journal_temp)
            title = tr.find("td", width="668")
            author = tr.find("td", width="111")
            pages = tr.find("td", width="42")
            if pages==None:
                pages = tr.find("td", width="43")
            a = pages.find("a")
            if "Page" in pages.get_text():
                continue
            info[Row_Name.TITLE]=title.get_text().strip()
            info[Row_Name.AUTHOR_NAME]=author.get_text().strip()
            pages=pages.get_text().strip().split("-")
            info[Row_Name.START_PAGE]=pages[0]
            info[Row_Name.END_PAGE]=pages[1]
            try:
                info[Row_Name.PAGE_TOTAL]=int(pages[1])-int(pages[0])+1
            except:
                pass
            info[Row_Name.TEMP_AURL]="ddd"

            if a != None:
                f_url = a["href"]
                info[Row_Name.FULLTEXT_URL]=f_url
                info[Row_Name.ABS_URL]=data.url
                info[Row_Name.PAGEURL]=data.url
            urls.append(info)
        return urls

    def second(self,article_info):

        return article_info




if __name__ == '__main__':
    urls = []
    url="https://www.cambridge.org/core/journals/canadian-journal-of-emergency-medicine/all-issues"
    info={}
    h={"upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    }
    data = requests.get(url,headers=h)
    print(data.status_code)
    print(data.text)
    bs = BeautifulSoup(data.text, "html.parser")
    ul=bs.find("ul",class_="accordion nested-accordion")
    print(ul)











