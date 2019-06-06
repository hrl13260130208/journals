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
        journal_common_info[Row_Name.FILENAME] = "zxD20161121193457389"
        wait()

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2016"
        issue_info[Row_Name.VOLUME] = "16"
        issue_info[Row_Name.ISSUE] = "2016"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol16_2016.htm"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2014"
        issue_info[Row_Name.VOLUME] = "14"
        issue_info[Row_Name.ISSUE] = "1"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol14-1.htm"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2013"
        issue_info[Row_Name.VOLUME] = "13"
        issue_info[Row_Name.ISSUE] = "1"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol13_Malaya.htm"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2013"
        issue_info[Row_Name.VOLUME] = "13"
        issue_info[Row_Name.ISSUE] = "2"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol13_special.htm"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2012"
        issue_info[Row_Name.VOLUME] = "12"
        issue_info[Row_Name.ISSUE] = "2012"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol12"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2011"
        issue_info[Row_Name.VOLUME] = "11"
        issue_info[Row_Name.ISSUE] = "2011"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol11"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2010"
        issue_info[Row_Name.VOLUME] = "10"
        issue_info[Row_Name.ISSUE] = "2010"
        issue_info[Row_Name.TEMP_URL]="http://www.ejse.org/CurrentVol10.htm"

        self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1697-2694",Row_Name.EISSN:"2386-3803"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        for table in bs.find_all("table"):
            if table.find("table") != None:
                continue
            if "CONTENTS" in table.get_text():
                for tr in table.find_all("tr"):
                    info = dict(journal_temp)
                    tds = tr.find_all("td")
                    print(tds.__len__())

                    if tds.__len__() == 3:
                        if "CONTENTS" in tds[1].get_text():
                            continue
                        for span in tds[1].find_all("span"):
                            if span.find_all("a").__len__() == 1:
                                a = span.find("a")
                                info[Row_Name.TITLE] = a.get_text()
                                pdf_path = self.download_pdf("http://www.ejse.org/"+a["href"], "ejse")
                                if pdf_path != None:
                                    info[Row_Name.FULLTEXT_PDF] = pdf_path.replace(self.DOWNLOAD_DIR, "")
                                info[Row_Name.FULLTEXT_URL] = "http://www.ejse.org/"+a["href"]
                                info[Row_Name.PAGEURL] = data.url
                                info[Row_Name.ABS_URL] = data.url
                            i = span.find("i")
                            if i != None:
                                b = i.find("b")
                                if b != None:
                                    info[Row_Name.AUTHOR_NAME] = b.get_text().replace(",", "##")

                        pages = tds[2].get_text()
                        if "-" in pages:
                            pages = pages.split("-")
                            info[Row_Name.START_PAGE] = pages[0]
                            info[Row_Name.END_PAGE] = pages[1]
                            info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
                        else:
                            info[Row_Name.START_PAGE] = pages
                            info[Row_Name.END_PAGE] = pages
                            info[Row_Name.PAGE_TOTAL] = 1
                    info[Row_Name.TEMP_AURL]="dddddd"
                    urls.append(info)
        return urls

    def second(self,article_info):

        return article_info




if __name__ == '__main__':
    urls = []
    url="http://www.ejse.org/"
    journal_temp={}
    data = requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    for table in bs.find_all("table"):
        if table.find("table")!=None:
            continue
        if "CONTENTS" in table.get_text():
            for tr in table.find_all("tr"):
                info = dict(journal_temp)
                tds=tr.find_all("td")
                print(tds.__len__())

                if tds.__len__()==3:
                    if "CONTENTS" in tds[1].get_text():
                        continue
                    for span in tds[1].find_all("span"):
                        if span.find_all("a").__len__()==1:
                            a=span.find("a")
                            info[Row_Name.TITLE]=a.get_text().replace("\n","")
                            info[Row_Name.FULLTEXT_URL]=a["href"]
                            info[Row_Name.PAGEURL]=data.url
                            info[Row_Name.ABS_URL]=data.url
                        i = span.find("i")
                        if i != None:
                            b = i.find("b")
                            if b != None:
                                info[Row_Name.AUTHOR_NAME] = b.get_text().replace(",", "##")

                    pages=tds[2].get_text()
                    if "-" in pages:
                        pages = pages.split("-")
                        info[Row_Name.START_PAGE] = pages[0]
                        info[Row_Name.END_PAGE] = pages[1]
                        info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
                    else:
                        info[Row_Name.START_PAGE] = pages
                        info[Row_Name.END_PAGE] = pages
                        info[Row_Name.PAGE_TOTAL] = 1

                print(info)













