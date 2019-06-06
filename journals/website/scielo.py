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
        print(url)
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER] = website
        wait()

        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        for table in bs.find_all("table"):
            if table.find("table") == None:
                if "Vol" in table.get_text():
                    for tr in table.find_all("tr"):
                        if "Vol" in tr.get_text():
                            continue
                        year = ""
                        vol = ""
                        for td in tr.find_all("td"):
                            a = td.find("a")
                            print(a)
                            if a == None:
                                f = td.find("font")
                                if f != None:
                                    line = f.get_text().strip()
                                    if line.__len__() == 4:
                                        year = line
                                    elif line.__len__() == 2:
                                        vol = line
                            else:
                                issue_info = dict(journal_common_info)
                                issue_info[Row_Name.TEMP_URL] = a["href"]
                                issue_info[Row_Name.YEAR] = year
                                issue_info[Row_Name.VOLUME] = vol
                                issue_info[Row_Name.ISSUE] = a.get_text()
                                print(vol,a.get_text())
                                if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                                    self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0016-7169"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        for div in bs.find_all("div", align="left"):
            for a in div.find_all("a"):
                if "text" in a.get_text().lower():
                    info = dict(journal_temp)
                    info[Row_Name.TEMP_AURL]=a["href"]
                    urls.append(info)
        print(urls)
        return urls

    def second(self,article_info):
        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs = BeautifulSoup(data_s.text, "html.parser")

        doi = bs.find("meta", {"name": "citation_doi"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]

        article_title = bs.find("meta", {"name": "citation_title"})
        if article_title != None:
            article_info[Row_Name.TITLE] = article_title["content"]

        at = bs.find("p", class_="categoria")
        if at != None:
            article_info[Row_Name.ARTICLE_TYPE] = at.get_text()

        abs = bs.find("div", class_="abstract")
        if abs != None:
            text = abs.get_text().replace("ABSTRACT", "")
            if "Key words:" in text:
                abs_t = text[:text.find("Key words:")]
                keyword = text[text.find("Key words:") + 10:].replace(";", "##")
                article_info[Row_Name.ABSTRACT] = abs_t.replace("ABSTRACT", "")
                article_info[Row_Name.KEYWORD] = keyword

        spage = bs.find("meta", {"name": "citation_firstpage"})
        if spage != None:
            article_info[Row_Name.START_PAGE] = spage["content"]

        epage = bs.find("meta", {"name": "citation_lastpage"})
        if epage != None:
            article_info[Row_Name.END_PAGE] = epage["content"]

        if Row_Name.START_PAGE in article_info or Row_Name.END_PAGE in article_info:
            try:
                article_info[Row_Name.PAGE_TOTAL] = int(article_info[Row_Name.END_PAGE]) - int(
                    article_info[Row_Name.START_PAGE]) + 1
            except:
                pass

        pdate = bs.find("meta", {"name": "citation_date"})
        if pdate != None:
            article_info[Row_Name.STRING_PUB_DATE] = pdate["content"]

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.FULLTEXT_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url

        pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url != None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            pdf_path = self.download_pdf(pdf_url["content"], "scielo")
            if pdf_path != None:
                article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")

        corresp = bs.find("p", class_="corresp")
        if corresp != None:
            co = ""
            for a in corresp.find_all("a"):
                co += a.get_text()
            article_info[Row_Name.CORRESPONDING] = co

        affs = {}
        for ap in bs.find_all("p", class_="aff"):
            num = ap.find("sup").get_text()
            affs[num] = ap.get_text().replace(num, "")
        author_name = ""
        email = ""
        find_email = False
        affiliation = ""
        for author in bs.find_all("p", class_="author"):
            span = author.find("span")
            author_name += span.get_text() + "##"
            has_co = False
            for a in author.find_all("a"):
                a_text = a.get_text()
                if a_text in affs:
                    affiliation += affs[a_text] + "##"
                else:
                    has_co = True
                    find_email = True
                    email += co + "##"
            if not has_co:
                email += "$$##"

        article_info[Row_Name.AUTHOR_NAME] = author_name[:-2]
        if find_email:
            article_info[Row_Name.EMAIL] = email[:-2]
        article_info[Row_Name.AFFILIATION] = affiliation[:-2]
        return article_info




if __name__ == '__main__':
    urls = []
    url="http://www.scielo.org.mx/scielo.php?script=sci_arttext&pid=S0016-71692018000100039&lng=es&nrm=iso&tlng=en"
    article_info={}
    data_s = requests.get(url)
    bs = BeautifulSoup(data_s.text, "html.parser")

    doi = bs.find("meta", {"name": "citation_doi"})
    if doi != None:
        article_info[Row_Name.DOI] = doi["content"]

    article_title = bs.find("meta", {"name": "citation_title"})
    if article_title != None:
        article_info[Row_Name.TITLE] = article_title["content"]




    at=bs.find("p",class_="categoria")
    if at!=None:
        article_info[Row_Name.ARTICLE_TYPE]=at.get_text()

    abs = bs.find("div", class_="abstract")
    if abs != None:
        text=abs.get_text().replace("ABSTRACT","")
        if "Key words:" in text:
            abs_t=text[:text.find("Key words:")]
            keyword=text[text.find("Key words:")+10:].replace(";","##")
            article_info[Row_Name.ABSTRACT] = abs_t.replace("ABSTRACT","")
            article_info[Row_Name.KEYWORD] = keyword

    spage = bs.find("meta", {"name": "citation_firstpage"})
    if spage != None:
        article_info[Row_Name.START_PAGE] = spage["content"]

    epage = bs.find("meta", {"name": "citation_lastpage"})
    if epage != None:
        article_info[Row_Name.END_PAGE] = epage["content"]

    if Row_Name.START_PAGE in article_info or Row_Name.END_PAGE in article_info:
        try:
            article_info[Row_Name.PAGE_TOTAL]=int(article_info[Row_Name.END_PAGE])-int(article_info[Row_Name.START_PAGE])+1
        except:
            pass

    pdate = bs.find("meta", {"name": "citation_date"})
    if pdate != None:
        article_info[Row_Name.STRING_PUB_DATE] = pdate["content"]

    article_info[Row_Name.ABS_URL] = data_s.url
    article_info[Row_Name.FULLTEXT_URL] = data_s.url
    article_info[Row_Name.PAGEURL] = data_s.url

    corresp=bs.find("p",class_="corresp")
    if corresp!=None:
        co=""
        for a in corresp.find_all("a"):
            co+=a.get_text()
        article_info[Row_Name.CORRESPONDING]=co

    affs={}
    for ap in bs.find_all("p",class_="aff"):
        num=ap.find("sup").get_text()
        affs[num]=ap.get_text().replace(num,"")
    author_name=""
    email=""
    find_email=False
    affiliation=""
    for author in bs.find_all("p",class_="author"):
        span=author.find("span")
        author_name+=span.get_text()+"##"
        has_co=False
        for a in author.find_all("a"):
            a_text=a.get_text()
            if "*" in a_text:
                has_co=True
                find_email=True
                email+=co+"##"
            else:
                affiliation+=affs[a_text]+"##"
        if not has_co:
            email+="$$##"

    article_info[Row_Name.AUTHOR_NAME]=author_name[:-2]
    if find_email:
        article_info[Row_Name.EMAIL]=email[:-2]
    article_info[Row_Name.AFFILIATION]=affiliation[:-2]

    print(article_info)













