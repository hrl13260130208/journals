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
        journal_common_info[Row_Name.FILENAME]="N-IPP"
        for i in range(9):
            url = "https://iopscience.iop.org/volume/1674-1137/" + str(i+34)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
                'referer': 'link'}
            wait()
            data_s = requests.get(url, headers=headers, verify=False)
            bs = BeautifulSoup(data_s.text, "html.parser")
            h3 = bs.find("h3")
            strs = h3.get_text().split(",")
            vol = strs[0][6:]
            year = strs[1]
            div = bs.find("div", class_="mb-3")
            for li in div.find_all("li"):
                # article_info = dict(journal_temp)
                a = li.find("a")
                if a != None:
                    url = "https://iopscience.iop.org" + a["href"]
                    items = a.get_text().split(",")
                    issue = items[0][6:]
                    sdate = items[1]
                    article_info=dict(journal_common_info)
                    article_info[Row_Name.STRING_COVER_DATE] = sdate
                    article_info[Row_Name.ISSUE] = issue
                    article_info[Row_Name.VOLUME] = vol
                    article_info[Row_Name.YEAR] = year
                    article_info[Row_Name.TEMP_URL] = url
                    self.nm.save_journal_temp_data(journal,json.dumps(article_info))


    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1674-1137"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'referer': 'link'}
        data_s = requests.get(journal_temp[Row_Name.TEMP_URL], headers=headers, verify=False)
        bs = BeautifulSoup(data_s.text, "html.parser")

        div = bs.find("div", class_="art-list")
        for div_ in div.find_all("div", class_="art-list-item-body"):

            a = div_.find("a")
            if a != None:
                article_info = dict(journal_temp)
                url = "https://iopscience.iop.org" + a["href"]
                article_info[Row_Name.TEMP_AURL] = url
                urls.append(article_info)
        return urls

    def second(self,article_info):
        wait()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'referer': 'link'}
        data_s = requests.get(article_info[Row_Name.TEMP_AURL], headers=headers, verify=False)
        bs = BeautifulSoup(data_s.text, "html.parser")

        doi = bs.find("meta", {"name": "citation_doi"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]
        a_type = bs.find("meta", {"name": "dc.type"})
        if a_type != None:
            article_info[Row_Name.ARTICLE_TYPE] = a_type["content"]

        title = bs.find("meta", {"name": "citation_title"})
        if title != None:
            article_info[Row_Name.TITLE] = title["content"]

        article_info[Row_Name.LANGUAGE] = "en"

        abs = bs.find("div", class_="article-text wd-jnl-art-abstract cf")
        if abs != None:
            article_info[Row_Name.ABSTRACT] = abs.get_text().strip()

        pub_date = bs.find("meta", {"name": "citation_publication_date"})
        if pub_date != None:
            article_info[Row_Name.STRING_PUB_DATE] = pub_date["content"]

        online_date = bs.find("meta", {"name": "citation_online_date"})
        if online_date != None:
            article_info[Row_Name.ONLINE_DATE] = online_date["content"]

        copyright = bs.find("span", {"itemprop": "copyrightHolder"})
        if copyright != None:
            article_info[Row_Name.COPYRIGHT_STATEMENT] = copyright.get_text().strip()
            year = re.search("\d{4}", copyright.get_text())
            if year != None:
                article_info[Row_Name.COPYRIGHT_YEAR] = year.group()
                article_info[Row_Name.COPYRIGHT_HOLDER] = copyright.get_text().replace(year.group(), "").replace("©",
                                                                                                                 "").strip()
            else:
                article_info[Row_Name.COPYRIGHT_HOLDER] = copyright.get_text().replace("©", "").srtip()

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url
        pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url != None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            try:
                pdf_path = self.download_pdf(pdf_url["content"], "N-IPP")
                if pdf_path != None:
                    article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
            except:
                article_info[Row_Name.FULLTEXT_PDF]=""
        aff_dict = {}
        aff_div = bs.find("div", class_="wd-jnl-art-author-affiliations")
        for aff in aff_div.find_all("p", class_="mb-05"):
            sup = aff.find("sup")
            if sup != None:
                key = sup.get_text()
                sup.extract()
                aff_dict[key] = aff.get_text()

        email_div = bs.find("div", class_="wd-jnl-art-email-addresses")
        email = ""
        for ea in email_div.find_all("a"):
            email += ea.get_text().strip() + "##"

        article_info[Row_Name.EMAIL] = email[:-2]
        author_name = ""
        author_aff = ""
        for au in bs.find_all("span", itemprop="author"):
            author = au.find("span", itemprop="name")
            print(author)
            if author != None:
                au_sups = au.find("sup")
                au_aff = ""
                if au_sups != None:
                    for au_sup in au_sups.get_text().split(","):
                        if au_sup in aff_dict:
                            au_aff = aff_dict[au_sup] + ";"
                    au_aff = au_aff[:-1]
                else:
                    au_aff = "$$"

                author_name += author.get_text().strip() + "##"
                author_aff += au_aff + "##"

        article_info[Row_Name.AUTHOR_NAME] = author_name[:-2]
        article_info[Row_Name.AFFILIATION] = author_aff[:-2]
        return article_info




if __name__ == '__main__':
    urls = []
    url="https://iopscience.iop.org/article/10.1088/1674-1137/42/12/124104"
    article_info={}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
               'referer': 'link'}
    data_s = requests.get(url, headers=headers,verify=False)
    bs = BeautifulSoup(data_s.text, "html.parser")

    doi = bs.find("meta", {"name": "citation_doi"})
    if doi != None:
        article_info[Row_Name.DOI] = doi["content"]
    a_type = bs.find("meta", {"name": "dc.type"})
    if a_type != None:
        article_info[Row_Name.ARTICLE_TYPE] = a_type["content"]



    title = bs.find("meta", {"name": "citation_title"})
    if title != None:
        article_info[Row_Name.TITLE] = title["content"]

    article_info[Row_Name.LANGUAGE] = "en"

    abs = bs.find("div", class_="article-text wd-jnl-art-abstract cf")
    if abs != None:
        article_info[Row_Name.ABSTRACT] = abs.get_text().strip()

    pub_date = bs.find("meta", {"name": "citation_publication_date"})
    if pub_date != None:
        article_info[Row_Name.STRING_PUB_DATE] = pub_date["content"]

    online_date = bs.find("meta", {"name": "citation_online_date"})
    if pub_date != None:
        article_info[Row_Name.STRING_PUB_DATE] = pub_date["content"]

    copyright = bs.find("span", {"itemprop": "copyrightHolder"})
    if copyright != None:
        article_info[Row_Name.COPYRIGHT_STATEMENT] = copyright.get_text().strip()
        year = re.search("\d{4}", copyright.get_text())
        if year != None:
            article_info[Row_Name.COPYRIGHT_YEAR] = year.group()
            article_info[Row_Name.COPYRIGHT_HOLDER] = copyright.get_text().replace(year.group(), "").replace("©","").strip()
        else:
            article_info[Row_Name.COPYRIGHT_HOLDER] = copyright.get_text().replace("©","").srtip()

    article_info[Row_Name.ABS_URL] = data_s.url
    article_info[Row_Name.PAGEURL] = data_s.url
    pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
    if pdf_url != None:
        article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
        # pdf_path = self.download_pdf(pdf_url["content"], "N-Nature")
        # if pdf_path != None:
        #     article_info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
    aff_dict={}
    aff_div = bs.find("div", class_="wd-jnl-art-author-affiliations")
    for aff in aff_div.find_all("p", class_="mb-05"):
        sup = aff.find("sup")
        if sup != None:
            key = sup.get_text()
            sup.extract()
            aff_dict[key] = aff.get_text()

    email_div = bs.find("div", class_="wd-jnl-art-email-addresses")
    email=""
    for ea in email_div.find_all("a"):
        email+=ea.get_text().strip()+"##"

    article_info[Row_Name.EMAIL]=email[:-2]
    author_name=""
    author_aff=""
    for au in bs.find_all("span",itemprop="author"):
        author=au.find("span",itemprop="name")
        print(author)
        if author!=None:
            au_sups=au.find("sup")
            au_aff=""
            if au_sups!=None:
                for au_sup in au_sups.get_text().split(","):
                    if au_sup in aff_dict:
                        au_aff=aff_dict[au_sup]+";"
                au_aff=au_aff[:-1]
            else:
                au_aff="$$"

            author_name+=author.get_text().strip()+"##"
            author_aff+=au_aff+"##"

    article_info[Row_Name.AUTHOR_NAME]=author_name[:-2]
    article_info[Row_Name.AFFILIATION]=author_aff[:-2]


    print(article_info)











