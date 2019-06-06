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
        journal_common_info[Row_Name.FILENAME]="zxD20161121193503212"
        wait()
        data_s = requests.get(url)
        soup = BeautifulSoup(data_s.text, "html.parser")
        div = soup.find("div", class_="art-postcontent art-postcontent-0 clearfix")
        for a in div.find_all("a"):
            new_url = a["href"]
            journal_common_info[Row_Name.TEMP_URL]=new_url
            print(journal_common_info)
            self.nm.save_journal_temp_data(journal,json.dumps(journal_common_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"2200-5390",Row_Name.EISSN:"2200-5404"}


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
    url="https://www.nature.com/labinvest/volumes/94/issues/1"
    article_info={}
    data_s = requests.get(url)
    bs = BeautifulSoup(data_s.text, "html.parser")
    div = bs.find("div", class_="container cleared container-type-article-grid-with-inset")

    for div_ in div.find_all("section"):
        # article_info = dict(journal_temp)
        for a in div_.find_all("a"):
            if a != None:
                article_info[Row_Name.TEMP_AURL] = "https://www.nature.com" + a["href"]


                print(article_info)









