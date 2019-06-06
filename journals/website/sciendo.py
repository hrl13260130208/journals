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
        journal_common_info[Row_Name.FILENAME]="zxD20160923093314187"



        new_url = "https://content.sciendo.com/view/journals/ring/33/1-2/ring.33.issue-1-2.xml"
        journal_common_info[Row_Name.TEMP_URL]=new_url
        print(journal_common_info)
        self.nm.save_journal_temp_data(journal,json.dumps(journal_common_info))
        new_url = "https://content.sciendo.com/view/journals/ring/35/1/ring.35.issue-1.xml"
        journal_common_info[Row_Name.TEMP_URL]=new_url
        print(journal_common_info)
        self.nm.save_journal_temp_data(journal,json.dumps(journal_common_info))
        new_url = "https://content.sciendo.com/view/journals/ring/36/1/ring.36.issue-1.xml"
        journal_common_info[Row_Name.TEMP_URL]=new_url
        print(journal_common_info)
        self.nm.save_journal_temp_data(journal,json.dumps(journal_common_info))
        new_url = "https://content.sciendo.com/view/journals/ring/37/1/ring.37.issue-1.xml"
        journal_common_info[Row_Name.TEMP_URL]=new_url
        print(journal_common_info)
        self.nm.save_journal_temp_data(journal,json.dumps(journal_common_info))
        new_url = "https://content.sciendo.com/view/journals/ring/38/1/ring.38.issue-1.xml"
        journal_common_info[Row_Name.TEMP_URL] = new_url
        print(journal_common_info)
        self.nm.save_journal_temp_data(journal, json.dumps(journal_common_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0035-5429",Row_Name.EISSN:"2083-3520"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data_s = requests.get(journal_temp[Row_Name.TEMP_URL], headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"},
                              verify=False)
        bs = BeautifulSoup(data_s.text, "html.parser")
        ul = bs.find("ul", class_="tree collapsible-tree expand-all ")
        for li in ul.find_all("li"):
            div1 = li.find("div", class_="label")
            [div.extract() for div in div1.find("div", class_="s-pr-4")]
            article_info = dict(journal_temp)
            a = div1.find("a")
            new_url = "https://content.sciendo.com" + a["href"]
            article_info[Row_Name.TEMP_AURL] = new_url
            urls.append(article_info)
                # if pdf_path != None:
                #     article_info=dict(journal_temp)
                #     article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
                #     article_info[Row_Name.FULLTEXT_URL]=pdf_url
                #     article_info[Row_Name.ABS_URL]=data.url
                #     article_info[Row_Name.TEMP_AURL]=data.url
                #     urls.append(article_info)

        return urls

    def second(self,article_info):
        data_s = requests.get(article_info[Row_Name.TEMP_AURL], headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"},
                              verify=False )
        bs = BeautifulSoup(data_s.text, "html.parser")
        pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url != None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            pdf_path = self.download_pdf(pdf_url["content"], "sciendo0523")
            if pdf_path != None:
                article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
        return article_info




if __name__ == '__main__':
    urls = []
    url="https://content.sciendo.com/view/journals/ring/36/1/article-p45.xml"
    article_info={}
    data_s = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"})
    bs = BeautifulSoup(data_s.text, "html.parser")
    for a in bs.find_all("a"):
        if a.get_text()=="":
            pass
    # div = bs.find("div", class_="container cleared container-type-article-grid-with-inset")
    #
    # for div_ in div.find_all("section"):
    #     # article_info = dict(journal_temp)
    #     for a in div_.find_all("a"):
    #         if a != None:
    #             article_info[Row_Name.TEMP_AURL] = "https://www.nature.com" + a["href"]
    #
    #
    #             print(article_info)









