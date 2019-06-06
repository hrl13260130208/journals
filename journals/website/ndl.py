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
        journal_common_info[Row_Name.FILENAME]="zxD20161026172842570"
        wait()

        for i in range(9):
            article_info=dict(journal_common_info)
            article_info[Row_Name.VOLUME] = str(i+2010)
            article_info[Row_Name.YEAR] = str(i+2010)
            article_info[Row_Name.TEMP_URL] = "https://www.ndl.go.jp/en/publication/ndl_newsletter/backno"+str(i+2010)+".html"

            self.nm.save_journal_temp_data(journal,json.dumps(article_info))


    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0027-9161",Row_Name.EISSN:"1344-7238"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        h3s = bs.find_all("h3")
        divs = bs.find_all("div", class_="section")
        delete = []
        for d in divs:
            if d.find("ul") == None:
                delete.append(d)

        for d in delete:
            divs.remove(d)

        if h3s.__len__() == divs.__len__():
            for i in range(h3s.__len__()):
                h3 = h3s[i]
                [a.extract() for a in h3.find_all("a")]
                line = h3.get_text()
                args = line.split(",")
                if len(args) == 2:
                    issue = args[0]
                    sdate = args[1]
                div = divs[i]
                for a in div.find_all("a"):
                    article_info = dict(journal_temp)
                    if "http" in a["href"]:
                        article_info[Row_Name.TEMP_AURL]=a["href"]
                    else:
                        article_info[Row_Name.TEMP_AURL]="http://dl.ndl.go.jp"+a["href"]
                    article_info[Row_Name.TITLE]=a.get_text()
                    article_info[Row_Name.STRING_COVER_DATE]=sdate
                    article_info[Row_Name.ISSUE]=issue

                    urls.append(article_info)
        return urls

    def second(self,article_info):
        wait()
        if "pdf" in  article_info[Row_Name.TEMP_AURL]:
            article_info[Row_Name.FULLTEXT_URL] = article_info[Row_Name.TEMP_AURL]
            pdf_path = self.download_pdf(article_info[Row_Name.TEMP_AURL], "zxD20161026172842570")
            if pdf_path != None:
                article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
            return article_info

        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs = BeautifulSoup(data_s.text, "html.parser")

        description = bs.find("meta", {"name": "description"})
        if description != None:
            article_info[Row_Name.ARTICLE_TYPE] = description["content"]

        doi = bs.find("meta", {"name": "citation_doi"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]

        title = bs.find("meta", {"name": "citation_title"})
        if title != None:
            article_info[Row_Name.TITLE] = title["content"]

        article_info[Row_Name.LANGUAGE] = "en"

        abs = bs.find("div", id="abstract-content")
        if abs != None:
            article_info[Row_Name.ABSTRACT] = abs.get_text().strip()

        start_page = bs.find("meta", {"name": "citation_firstpage"})
        if start_page != None:
            article_info[Row_Name.START_PAGE] = start_page["content"]

        end_page = bs.find("span", itemprop="pageEnd")
        if end_page != None:
            article_info[Row_Name.END_PAGE] = end_page.get_text()

        if end_page != None and start_page != None:
            try:
                article_info[Row_Name.PAGE_TOTAL] = int(end_page.get_text()) - int(start_page["content"]) + 1
            except:
                pass

        pub_date = bs.find("meta", {"name": "prism.publicationDate"})
        if pub_date != None:
            article_info[Row_Name.STRING_PUB_DATE] = pub_date["content"]
        copyright = bs.find("meta", {"name": "dc.copyright"})
        if copyright != None:
            article_info[Row_Name.COPYRIGHT_STATEMENT] = copyright["content"]
            year = re.search("\d{4}", copyright["content"])
            if year != None:
                article_info[Row_Name.COPYRIGHT_YEAR] = year.group()
                article_info[Row_Name.COPYRIGHT_HOLDER] = copyright["content"].replace(year.group(), "")
            else:
                article_info[Row_Name.COPYRIGHT_HOLDER] = copyright["content"]

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url
        pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url != None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            pdf_path = self.download_pdf(pdf_url["content"], "N-Nature")
            if pdf_path != None:
                article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")

        au = ""
        af = ""
        for li in bs.find_all("li", itemprop="author"):
            a = li.find("a")
            if a != None:
                au += a.get_text().strip() + "##"
            aff = li.find("meta", {"itemprop": "address"})
            if aff != None:
                af += aff["content"].strip() + "##"

        if au != "":
            article_info[Row_Name.AUTHOR_NAME] = au[:-2]
        if af != None:
            article_info[Row_Name.AFFILIATION] = af[:-2]
        return article_info




if __name__ == '__main__':
    url="https://www.ndl.go.jp/en/publication/ndl_newsletter/215/21504.html"
    article_info={}
    data_s = requests.get(url)
    bs = BeautifulSoup(data_s.text, "html.parser")


    print(article_info)







