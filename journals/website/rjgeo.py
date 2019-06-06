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
        journal_common_info[Row_Name.FILENAME]="1-RAPH-53027"
        wait()
        url = "http://www.rjgeo.ro/past_issues.html"

        data_s = requests.get(url)
        bs = BeautifulSoup(data_s.text, "html.parser")

        for a in bs.find_all("a"):
            # article_info = dict(journal_temp)
            text = a.get_text()
            if "2010" in text or "2011" in text or "2012" in text or "2016" in text:
                new_url = "http://www.rjgeo.ro/" + a["href"]
                article_info = dict(journal_common_info)
                article_info[Row_Name.TEMP_URL]=new_url
                self.nm.save_journal_temp_data(journal,json.dumps(article_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1220-5311",Row_Name.EISSN:"2285-9675"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        print(journal_temp)
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")

        for a in bs.find_all("a"):
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
    url="http://www.rjgeo.ro/revue%2054_2.html"
    article_info={}
    data_s = requests.get(url)
    bs = BeautifulSoup(data_s.text, "html.parser")

    for a in bs.find_all("a"):
        # article_info = dict(journal_temp)
        text=a.get_text()
        if "2010" in text or "2011" in text or "2012" in text or "2016" in text:
            url="http://www.rjgeo.ro/"+a["href"]
            print(url)









