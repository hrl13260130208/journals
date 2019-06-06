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
        journal_common_info[Row_Name.FILENAME] = "zxD20160815141800176"
        wait()

        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        ul = bs.find("ul", class_="issues")
        for li in ul.find_all("li"):
            h3 = li.find("h3")
            if h3 != None:
                args = h3.get_text().split(" ")
                vol = args[0]
                year = args[1][1:-1]
                for a in li.find_all("a"):
                    issue_info = dict(journal_common_info)
                    issue_info[Row_Name.TEMP_URL] = "https://journals.openedition.org/sdt/" + a["href"]
                    issue_info[Row_Name.YEAR] = year
                    issue_info[Row_Name.VOLUME] = vol
                    issue_info[Row_Name.ISSUE] = a.get_text()
                    print(issue_info)

                    if year=="2017"or year=="2015":
                        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0038-0296"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        bs = BeautifulSoup(data.text, "html.parser")
        pli = bs.find("li", class_="publications even")
        ul = pli.find("ul")
        pli2 = bs.find("li", class_="publications odd")
        ul2 = pli2.find("ul")
        for li in ul.find_all("li"):
            info = dict(journal_temp)
            info[Row_Name.AUTHOR_NAME] = li.find("div", class_="author").get_text()
            div = li.find("div", class_="title")
            a = div.find("a")
            if a != None:
                info[Row_Name.TEMP_AURL] = "https://journals.openedition.org/sdt/" + a["href"]
            urls.append(info)
        for li2 in ul2.find_all("li"):
            info = dict(journal_temp)
            info[Row_Name.AUTHOR_NAME] = li2.find("div", class_="author").get_text()
            div = li2.find("div", class_="title")
            a = div.find("a")
            if a != None:
                info[Row_Name.TEMP_AURL] = "https://journals.openedition.org/sdt/" + a["href"]
            urls.append(info)
        return urls

    def second(self,article_info):
        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs = BeautifulSoup(data_s.text, "html.parser")

        doi = bs.find("meta", {"scheme": "DOI"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]

        a_type = bs.find("meta", {"name": "DC.type"})
        if a_type != None:
            article_info[Row_Name.ARTICLE_TYPE] = a_type["content"]

        article_title = bs.find("meta", {"name": "citation_title"})
        if article_title != None:
            article_info[Row_Name.TITLE] = article_title["content"]

        keywords = bs.find("meta", {"name": "citation_keywords"})
        if keywords != None:
            article_info[Row_Name.KEYWORD] = keywords["content"].replace(";", "##")
        abs = bs.find("meta", {"name": "citation_abstract"})
        if abs != None:
            article_info[Row_Name.ABSTRACT] = abs["content"].replace("\n"," ").strip()

        pdate = bs.find("meta", {"name": "citation_publication_date"})
        if pdate != None:
            article_info[Row_Name.STRING_PUB_DATE] = pdate["content"]

        article_info[Row_Name.LANGUAGE] = "fr"

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.FULLTEXT_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url

        pdf_path = self.download_html(data_s.url, "openedition")
        if pdf_path != None:
            article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
        return article_info




if __name__ == '__main__':
    urls = []
    url="https://journals.openedition.org/sdt/14517"
    article_info={}
    data_s = requests.get(url)
    bs = BeautifulSoup(data_s.text, "html.parser")

    doi = bs.find("meta", {"scheme": "DOI"})
    if doi != None:
        article_info[Row_Name.DOI] = doi["content"]

    a_type = bs.find("meta", {"name": "DC.type"})
    if a_type != None:
        article_info[Row_Name.ARTICLE_TYPE] = a_type["content"]

    article_title = bs.find("meta", {"name": "citation_title"})
    if article_title != None:
        article_info[Row_Name.TITLE] = article_title.get_text().strip()

    keywords = bs.find("meta", {"name": "citation_keywords"})
    if keywords != None:
        article_info[Row_Name.KEYWORD] = keywords["content"].replace(";","##")
    abs = bs.find("meta", {"name": "citation_abstract"})
    if abs != None:
        article_info[Row_Name.ABSTRACT] = abs["content"]

    pdate = bs.find("meta", {"name": "citation_publication_date"})
    if pdate != None:
        article_info[Row_Name.STRING_PUB_DATE] = pdate["content"]



    article_info[Row_Name.LANGUAGE]="fr"

    article_info[Row_Name.ABS_URL] = data_s.url
    article_info[Row_Name.FULLTEXT_URL] = data_s.url
    article_info[Row_Name.PAGEURL] = data_s.url

    print(article_info)
    #
    # article_info[Row_Name.KEYWORD] = keywords[:-2]
    #
    # abs = bs.find("div", class_="article-details-block article-details-abstract")
    # if abs != None:
    #     article_info[Row_Name.ABSTRACT] = abs.get_text()
    #

    # author_name = ""
    # aff = ""
    # for i in range(20):
    #     a_div = bs.find("div", id="author-" + str(i + 1))
    #     if a_div == None:
    #         break
    #     an = a_div.find("div", class_="article-details-author-name small-screen")
    #     if an != None:
    #         author_name += an.get_text().replace("\n", "").strip() + "##"
    #         af = a_div.find("div", class_="article-details-author-affiliation")
    #         if af == None:
    #             aff += "$$##"
    #         else:
    #             aff += af.get_text() + "##"
    #
    # article_info[Row_Name.AUTHOR_NAME] = author_name[:-2]
    # article_info[Row_Name.AFFILIATION] = aff[:-2]
    #







