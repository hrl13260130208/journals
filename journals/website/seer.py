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
        journal_common_info[Row_Name.FILENAME] = "zxD20161205102207499"
        wait()
        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2017"
        issue_info[Row_Name.TEMP_URL] ="http://www.seer.ufu.br/index.php/sociedadenatureza/issue/view/1519"
        issue_info[Row_Name.VOLUME] = "29"
        issue_info[Row_Name.ISSUE] = "2"
        self.nm.save_journal_temp_data(journal, json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2017"
        issue_info[Row_Name.TEMP_URL] ="http://www.seer.ufu.br/index.php/sociedadenatureza/issue/view/1559"
        issue_info[Row_Name.VOLUME] = "29"
        issue_info[Row_Name.ISSUE] = "3"
        self.nm.save_journal_temp_data(journal, json.dumps(issue_info))

        # data = requests.get(url)
        # bs = BeautifulSoup(data.text, "html.parser")
        # for div in bs.find_all("div", class_="col-md-3 col-lg-2"):
        #     issue_info = dict(journal_common_info)
        #     h2 = div.find("h2")
        #     tt = h2.get_text()
        #     if "vol" in tt.lower():
        #         volume = re.search("\d+", re.search("Vol.+\d+", tt).group()).group()
        #         no = re.search("\d+", re.search("No.+\d+", tt).group()).group()
        #         cdate = re.search("\(\d{4}\)", tt).group()
        #         year = re.search("\d+", cdate).group()
        #
        #         issue_info[Row_Name.YEAR] = year
        #         issue_info[Row_Name.VOLUME] = volume
        #         issue_info[Row_Name.ISSUE] = no
        #         a = h2.find("a")
        #         if a != None:
        #             issue_info[Row_Name.TEMP_URL] = a["href"]
        #
        #         if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
        #             self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0103-1570",Row_Name.EISSN:"1982-4513"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", class_="issue-toc-section")

        for div_ in div.find_all("div", class_="article-summary-title"):
            info = dict(journal_temp)
            a = div_.find("a")
            if a != None:
                info[Row_Name.TEMP_AURL] = a["href"]
            urls.append(info)
        return urls

    def second(self,article_info):
        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs = BeautifulSoup(data_s.text, "html.parser")

        doi = bs.find("meta", {"name": "citation_doi"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]

        cdate = bs.find("meta", {"name": "citation_date"})
        if cdate != None:
            article_info[Row_Name.STRING_PUB_DATE] = cdate["content"]

        article_title = bs.find("h1")
        if article_title != None:
            article_info[Row_Name.TITLE] = article_title.get_text().strip()
        keywords = ""
        for keyword in bs.find_all("meta", {"name": "citation_keywords"}):
            keywords += keyword["content"] + "##"

        article_info[Row_Name.KEYWORD] = keywords[:-2]

        abs = bs.find("div", class_="article-details-block article-details-abstract")
        if abs != None:
            article_info[Row_Name.ABSTRACT] = abs.get_text()

        article_info[Row_Name.ABS_URL] = data_s.url

        article_info[Row_Name.PAGEURL] = data_s.url
        pdf_url= bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url!=None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            pdf_path = self.download_pdf(pdf_url["content"], "seer")
            if pdf_path != None:
                article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
        author_name = ""
        aff = ""
        for i in range(20):
            a_div = bs.find("div", id="author-" + str(i + 1))
            if a_div == None:
                break
            an = a_div.find("div", class_="article-details-author-name small-screen")
            if an != None:
                author_name += an.get_text().replace("\n", "").strip() + "##"
                af = a_div.find("div", class_="article-details-author-affiliation")
                if af == None:
                    aff += "$$##"
                else:
                    aff += af.get_text() + "##"

        article_info[Row_Name.AUTHOR_NAME] = author_name[:-2]
        article_info[Row_Name.AFFILIATION] = aff[:-2]
        return article_info




if __name__ == '__main__':
    urls = []
    url="http://www.seer.ufu.br/index.php/sociedadenatureza/article/view/46576"
    article_info={}
    data_s = requests.get(article_info[Row_Name.TEMP_AURL])
    bs = BeautifulSoup(data_s.text, "html.parser")

    doi = bs.find("meta", {"name": "citation_doi"})
    if doi != None:
        article_info[Row_Name.DOI] = doi["content"]

    cdate = bs.find("meta", {"name": "citation_date"})
    if cdate != None:
        article_info[Row_Name.STRING_PUB_DATE] = cdate["content"]

    article_title = bs.find("h1")
    if article_title != None:
        article_info[Row_Name.TITLE] = article_title.get_text().strip()
    keywords=""
    for keyword in  bs.find_all("meta", {"name": "citation_keywords"}):

        keywords+=keyword["content"]+"##"

    article_info[Row_Name.KEYWORD]=keywords[:-2]

    abs=bs.find("div",class_="article-details-block article-details-abstract")
    if abs!=None:
        article_info[Row_Name.ABSTRACT]=abs.get_text()

    article_info[Row_Name.ABS_URL] = data_s.url
    article_info[Row_Name.FULLTEXT_URL] = data_s.url
    article_info[Row_Name.PAGEURL] = data_s.url
    author_name=""
    aff=""
    for i in range(20):
        a_div=bs.find("div",id="author-"+str(i+1))
        if a_div==None:
            break
        an=a_div.find("div",class_="article-details-author-name small-screen")
        if an!=None:
            author_name+=an.get_text().replace("\n","").strip()+"##"
            af=a_div.find("div",class_="article-details-author-affiliation")
            if af==None:
                aff+="$$##"
            else:
                aff+=af.get_text()+"##"

    article_info[Row_Name.AUTHOR_NAME]=author_name[:-2]
    article_info[Row_Name.AFFILIATION]=aff[:-2]
    print(article_info)









