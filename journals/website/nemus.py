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
        journal_common_info[Row_Name.FILENAME] = "zxD20161121193506263"

        issue_info = dict(journal_common_info)
        issue_info[Row_Name.YEAR] = "2016"
        issue_info[Row_Name.VOLUME] = "6"
        issue_info[Row_Name.ISSUE] = "1"
        issue_info[Row_Name.TEMP_URL]="http://ateneudenatura.uji.es/Nemus/Nemus6/nemus6.htm"
        self.nm.save_journal_temp_data(journal, json.dumps(issue_info))

        # wait()
        # data = requests.get(url)
        # # print(data.text)
        # bs = BeautifulSoup(data.text, "html.parser")
        # table = bs.find("table", width="100%")
        # for td in table.find_all("td"):
        #     a = td.find("a")
        #     font = td.find("font")
        #     if a != None and font != None:
        #         url = "http://ateneudenatura.uji.es/Nemus/" + a["href"]
        #         print(url)
        #         lfont = font.get_text()
        #         if "NÚMERO" in lfont:
        #             year = re.search("\d{4}", lfont)
        #             if year != None:
        #                 num = re.search("\d", lfont.replace(year.group(), ""))
        #                 if num != None:
        #                     issue_info = dict(journal_common_info)
        #                     issue_info[Row_Name.YEAR] = year.group()
        #                     issue_info[Row_Name.VOLUME] = num.group()
        #                     issue_info[Row_Name.ISSUE] = "1"
        #                     issue_info[Row_Name.TEMP_URL]=url
        #
        #                 if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
        #                     self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1697-2694",Row_Name.EISSN:"2386-3803"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        start = False
        s = 0
        info = None
        abstract = False
        keyword = False
        for p in bs.find_all("p"):
            text = p.get_text()
            if not start:
                if "ÍNDEX" in text:
                    start = True
            else:
                try:
                    style = p["style"]
                except:
                    pass

                if style == "margin-top: 0pt; margin-bottom: 0pt" or style == "margin-top: 0pt; margin-bottom: 0pt;":
                    a = p.find("a")
                    line = p.get_text().replace("\n", " ")
                    if a != None:
                        if a.get_text() != "":
                            if s == 0:
                                if info != None:
                                    urls.append(info)

                                info = dict(journal_temp)
                                info[Row_Name.TITLE] = a.get_text().replace("\n", " ")
                                f_url = data.url[:data.url.rfind("/") + 1] + a["href"]
                                info[Row_Name.ABS_URL]=data.url
                                info[Row_Name.PAGEURL]=data.url
                                info[Row_Name.FULLTEXT_URL]=f_url
                                file_path=self.download_pdf(f_url,"nemus")
                                if file_path!=None:
                                    info[Row_Name.FULLTEXT_PDF]=file_path.replace(self.DOWNLOAD_DIR,"")
                                info[Row_Name.TEMP_AURL]="ss"

                                s = 1
                            elif s == 1:
                                pass
                    elif "pp." in line:
                        b = p.find("b")
                        if b != None:
                            info[Row_Name.AUTHOR_NAME] = b.get_text().replace("\n", " ").replace("..", "").replace(",",
                                                                                                                   "##")
                        pages = line[line.find("pp.") + 3:]
                        if "-" in pages:
                            pages = pages.split("-")
                            info[Row_Name.START_PAGE] = pages[0]
                            info[Row_Name.END_PAGE] = pages[1]
                            try:
                                info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
                            except:
                                pass


                elif style == "line-height: 14.8pt; margin-top: 0pt; margin-bottom: 0pt;":
                    if s == 1:
                        s = 0
                    line = p.get_text().replace("\n", " ")
                    if "ABSTRACT" in line:
                        abstract = True
                    if abstract:
                        info[Row_Name.ABSTRACT] = line
                    if "Key words" in line:
                        info[Row_Name.KEYWORD] = line.replace(",", "##")
        if info != None:
            urls.append(info)
        return urls

    def second(self,article_info):
        print(article_info)
        return article_info



if __name__ == '__main__':


    urls = []
    url="http://ateneudenatura.uji.es/Nemus/Nemus8/nemus8.htm"
    journal_temp={}
    data = requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    start = False
    s = 0
    info = None
    abstract = False
    keyword = False
    for p in bs.find_all("p"):
        text = p.get_text()
        if not start:
            if "ÍNDEX" in text:
                start = True
        else:
            try:
                style = p["style"]
            except:
                pass

            if style == "margin-top: 0pt; margin-bottom: 0pt" or style == "margin-top: 0pt; margin-bottom: 0pt;":
                a = p.find("a")
                line = p.get_text().replace("\n", " ")
                if a != None:
                    if a.get_text() != "":
                        if s == 0:
                            if info != None:
                                urls.append(info)
                                print(info)
                            info = dict(journal_temp)
                            info[Row_Name.TITLE] = a.get_text().replace("\n", " ")
                            f_url = data.url[:data.url.rfind("/") + 1] + a["href"]
                            info[Row_Name.ABS_URL] = data.url
                            info[Row_Name.PAGEURL] = data.url
                            info[Row_Name.FULLTEXT_URL] = f_url
                            # file_path = self.download_pdf(f_url, "nemus")
                            # if file_path != None:
                            #     info[Row_Name.FULLTEXT_PDF] = file_path.replace(self.DOWNLOAD_DIR, "")
                            info[Row_Name.TEMP_AURL] = "ss"

                            s = 1
                        elif s == 1:
                            pass
                elif "pp." in line:
                    b = p.find("b")
                    if b != None:
                        info[Row_Name.AUTHOR_NAME] = b.get_text().replace("\n", " ").replace("..", "").replace(",",
                                                                                                               "##")
                    pages = line[line.find("pp.") + 3:]
                    if "-" in pages:
                        pages = pages.split("-")
                        info[Row_Name.START_PAGE] = pages[0]
                        info[Row_Name.END_PAGE] = pages[1]
                        try:
                            info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
                        except:
                            pass


            elif style == "line-height: 14.8pt; margin-top: 0pt; margin-bottom: 0pt;":
                if s == 1:
                    s = 0
                line = p.get_text().replace("\n", " ")
                print(line,"ABSTRACT" in line)
                if "ABSTRACT" in line:
                    abstract = True
                    continue
                if abstract:
                    info[Row_Name.ABSTRACT] = line
                    abstract=False
                    continue
                if "Key words" in line:
                    keyword=True
                    continue
                if keyword:
                    info[Row_Name.KEYWORD] = line.replace(",", "##")
                    keyword=False











