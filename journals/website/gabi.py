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
        journal_common_info[Row_Name.FILENAME]="zxD20160815194527669"
        wait()
        data_s = requests.get(url)
        soup = BeautifulSoup(data_s.text, "html.parser")
        soup = BeautifulSoup(data_s.text, "html.parser")
        div = soup.find("div", id="content")
        for a in div.find_all("a"):
            new_url = a["href"]
            # print(new_url)
            if "2015" in new_url or "2016" in new_url or "2017" in new_url:
                new_info=dict(journal_common_info)
                new_info[Row_Name.TEMP_URL]=new_url

                self.nm.save_journal_temp_data(journal,json.dumps(new_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"2033-6403"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        print(journal_temp)
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", id="bv_Text1")

        for a in bs.find_all("a"):

            if "Full Text PDF" in a.get_text():
                pdf_url="http://www.sciencej.com"+a["href"][1:]
                pdf_path = self.download_pdf(pdf_url, "0523")
                if pdf_path != None:
                    article_info=dict(journal_temp)
                    article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
                    article_info[Row_Name.FULLTEXT_URL]=pdf_url
                    article_info[Row_Name.ABS_URL]=data.url
                    article_info[Row_Name.TEMP_AURL]=data.url
                    urls.append(article_info)

        return urls

    def second(self,article_info):

        return article_info




if __name__ == '__main__':
    urls = []
    url="http://gabi-journal.net/issues/volume-6-year-2017-issue-2"
    data_s=requests.get(url)
    soup = BeautifulSoup(data_s.text, "html.parser")
    div = soup.find("div", id="issues-page")
    for a in div.find_all("a"):
        new_url = a["href"]
        data_1=requests.get(new_url)










