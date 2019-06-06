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
        # print(data.text)
        bs = BeautifulSoup(data.text, "html.parser")
        table = bs.find("table")
        year = None
        volume = None
        for td in table.find_all("td"):
            if td.find("b") != None:
                r_td = re.search("\d{4}", td.get_text())
                if r_td != None:
                    year = r_td.group()
                    print(year)
                elif "volume" in td.get_text().lower():
                    volume = td.get_text().lower().replace("volume", "").strip()
                    print(volume)
            else:
                a = td.find("a")
                if a != None:
                    if "issue" in a.get_text().lower():
                        issue_info = dict(journal_common_info)
                        s = a.get_text().lower()
                        issue = s[s.find("issue") + 5:s.find("pp.") - 2].strip()
                        url = "http://www1.montpellier.inra.fr/CBGP/acarologia/" + a["href"]
                        print(year, volume, issue, url)
                        issue_info[Row_Name.YEAR] = year
                        issue_info[Row_Name.VOLUME] = volume
                        issue_info[Row_Name.ISSUE] = issue
                        issue_info[Row_Name.TEMP_URL] = url

                        if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                            self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"0976-2612",Row_Name.EISSN:"2107-7207"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")

        for p in bs.find_all("p"):
            a = p.find("a")
            if a != None:
                if "article.php" in a["href"]:
                    article_info = dict(journal_temp)
                    article_info[Row_Name.TEMP_AURL]="http://www1.montpellier.inra.fr/CBGP/acarologia/" + a["href"]
                    urls.append(article_info)
        return urls

    def second(self,article_info):

        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs = BeautifulSoup(data_s.text, "html.parser")

        doi = bs.find("meta", {"name": "citation_doi"})
        if doi != None:
            article_info[Row_Name.DOI] = doi["content"]

        article_type = bs.find("meta", {"name": "DC.Type.articleType"})
        if article_type != None:
            article_info[Row_Name.ARTICLE_TYPE] = article_type["content"]

        article_title = bs.find("meta", {"name": "citation_title"})
        if article_title != None:
            article_info[Row_Name.TITLE] = article_title["content"]

        language = bs.find("meta", {"name": "Content-Language"})
        if language != None:
            article_info[Row_Name.LANGUAGE] = language["content"]

        abs = bs.find("meta", {"name": "DC.Description"})
        if abs != None:
            article_info[Row_Name.ABSTRACT] = abs["content"]

        keywords = bs.find_all("meta", {"name": "DC.Subject"})
        if keywords != None:
            keys=""
            for keyword in keywords:
                keys+=keyword["content"]+"##"

            article_info[Row_Name.KEYWORD] = keys[:-2]

        spage = bs.find("meta", {"name": "DC.citation.spage"})
        if spage != None:
            article_info[Row_Name.START_PAGE] = spage["content"]

        epage = bs.find("meta", {"name": "DC.citation.epage"})
        if epage != None:
            article_info[Row_Name.END_PAGE] = epage["content"]

        if epage != None and spage != None:
            try:
                article_info[Row_Name.PAGE_TOTAL] = int(epage) - int(spage) + 1
            except:
                pass

        pub_date = bs.find("meta", {"name": "prism.publicationDate"})
        if pub_date != None:
            article_info[Row_Name.STRING_COVER_DATE] = pub_date["content"]

        right = bs.find("meta", {"name": "DC.Rights"})
        if right != None:
            article_info[Row_Name.COPYRIGHT_STATEMENT] = right["content"]
            r_year = re.search("\d{4}", right["content"])
            if r_year != None:
                article_info[Row_Name.COPYRIGHT_YEAR] = r_year.group()
                article_info[Row_Name.COPYRIGHT_HOLDER] = right["content"].replace(r_year.group(), "").replace("Copyright (c)", "").strip()
            else:
                article_info[Row_Name.COPYRIGHT_HOLDER] = right["content"].replace("Copyright (c)", "").strip()

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.FULLTEXT_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url

        an = ""
        for author_name in bs.find_all("meta", {"name": "citation_author"}):
            if author_name["content"] == "":
                an += "$$##"
            else:
                an += author_name["content"] + "##"

        article_info[Row_Name.AUTHOR_NAME] = an[:-2]

        af = ""
        for aff in bs.find_all("meta", {"name": "citation_author_institution"}):
            if aff["content"] == "":
                af += "$$##"
            else:
                af += aff["content"] + "##"

        article_info[Row_Name.AFFILIATION] = af[:-2]
        pdf_url = bs.find("meta", {"name": "citation_pdf_url"})
        if pdf_url != None:
            article_info[Row_Name.FULLTEXT_URL] = pdf_url["content"]
            pdf_path=self.download_pdf(pdf_url["content"],"acarologia")
            if pdf_path !=None:
                article_info[Row_Name.FULLTEXT_PDF]=pdf_path.replace(self.DOWNLOAD_DIR,"")
            else:
                print("pdf下载出错。")


        return article_info




if __name__ == '__main__':
    url="http://www1.montpellier.inra.fr/CBGP/acarologia/article.php?id=4281"
    article_info={}
    data=requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    keywords = bs.find_all("meta", {"name": "DC.Subject"})
    if keywords != None:
        keys = ""
        for keyword in keywords:
            keys += keyword["content"] + "##"

        article_info[Row_Name.KEYWORD] = keys[:-2]

    print(article_info)









