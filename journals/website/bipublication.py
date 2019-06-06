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
        bs = BeautifulSoup(data.text, "html.parser")

        div = bs.find("div", id="text2")
        div1 = div.find("div", class_="wpmd")
        # print(div1)
        for div_tag in div1.find_all("div"):
            if "Vol" in div_tag.get_text():
                year = None
                for font in div_tag.find_all("font"):
                    f_line = font.get_text()
                    year_f = re.search("\d{4}", f_line)
                    if year_f != None:
                        year = year_f.group()
                    if "Vol" in f_line:
                        a = font.find("a")
                        if a != None:
                            strings = f_line.split(",")
                            vol = strings[0].replace("Vol", "").strip()
                            issue = strings[1].replace("Issue", "").strip()
                            n_url = "http://bipublication.com/" + a['href']
                            issue_info = dict(journal_common_info)
                            issue_info[Row_Name.YEAR] = year
                            issue_info[Row_Name.VOLUME] = vol
                            issue_info[Row_Name.ISSUE] = issue
                            issue_info[Row_Name.TEMP_URL]=n_url

                        if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                            self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        return {Row_Name.ISSN:"1697-2694",Row_Name.EISSN:"2386-3803"}


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", id="table1")
        # print(div)
        table = div.find("table")
        for tr in table.find_all("tr"):
            info=dict(journal_temp)
            tds = tr.find_all("td")
            title = tds[1]
            author = tds[2]
            pages = tds[3]

            a = pages.find("a")
            if "Page" in pages.get_text():
                continue
            info[Row_Name.TITLE]=title.get_text().strip()
            info[Row_Name.AUTHOR_NAME]=author.get_text().strip()
            pages=pages.get_text().strip().split("-")
            info[Row_Name.START_PAGE]=pages[0]
            info[Row_Name.END_PAGE]=pages[1]
            try:
                info[Row_Name.PAGE_TOTAL]=int(pages[1])-int(pages[0])+1
            except:
                pass
            info[Row_Name.TEMP_AURL]="ddd"

            if a != None:
                f_url = a["href"]
                info[Row_Name.FULLTEXT_URL] = f_url
                if "https:" in f_url:
                    file_path = self.download_html(journal_temp[Row_Name.TEMP_URL], "bipublication")
                    if file_path != None:
                        info[Row_Name.FULLTEXT_PDF] = file_path.replace(self.DOWNLOAD_DIR, "")
                else:
                    f_url="http://bipublication.com/"+a["href"]
                    file_path=self.download_pdf(f_url,"bipublication")
                    if file_path!=None:
                        info[Row_Name.FULLTEXT_PDF]=file_path.replace(self.DOWNLOAD_DIR,"")
                info[Row_Name.ABS_URL]=data.url
                info[Row_Name.PAGEURL]=data.url
            urls.append(info)
        return urls

    def second(self,article_info):

        return article_info




if __name__ == '__main__':
    urls = []
    url="http://bipublication.com/ijabr93.html"
    info={}
    data = requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    div =bs.find("div",id="table1")
    table=div.find("table")
    for tr in table.find_all("tr"):
        tds=tr.find_all("td")
        title=tds[1]
        author=tds[2]
        pages=tds[3]
        # title=tr.find("td",width="668")
        # author=tr.find("td",width="111")
        # pages=tr.find("td",width="42")
        if "Page" in pages.get_text():
            continue

        a=pages.find("a")
        # print(pages)
        pages = pages.get_text().strip().split("-")
        info[Row_Name.START_PAGE] = pages[0]
        info[Row_Name.END_PAGE] = pages[1]
        try:
            info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
        except:
            pass
        if a!=None:
            f_url=a["href"]
            print(f_url)

        print(info)
    # start = False
    # s = 0
    # info = None
    # abstract = False
    # keyword = False
    # for p in bs.find_all("p"):
    #     text = p.get_text()
    #     if not start:
    #         if "ÍNDEX" in text:
    #             start = True
    #     else:
    #         try:
    #             style = p["style"]
    #         except:
    #             pass
    #
    #         if style == "margin-top: 0pt; margin-bottom: 0pt" or style == "margin-top: 0pt; margin-bottom: 0pt;":
    #             a = p.find("a")
    #             line = p.get_text().replace("\n", " ")
    #             if a != None:
    #                 if a.get_text() != "":
    #                     if s == 0:
    #                         if info != None:
    #                             urls.append(info)
    #                         info = {}
    #                         info[Row_Name.TITLE] = a.get_text().replace("\n", " ")
    #                         info[Row_Name.ABS_URL] = data.url
    #                         info[Row_Name.PAGEURL] = data.url
    #                         info[Row_Name.FULLTEXT_URL] = data.url
    #
    #                         s = 1
    #                     elif s == 1:
    #                         pass
    #             elif "pp." in line:
    #                 b = p.find("b")
    #                 if b != None:
    #                     info[Row_Name.AUTHOR_NAME] = b.get_text().replace("\n", " ").replace("..", "").replace(",",
    #                                                                                                            "##")
    #                 pages = line[line.find("pp.") + 3:]
    #                 if "-" in pages:
    #                     pages = pages.split("-")
    #                     info[Row_Name.START_PAGE] = pages[0]
    #                     info[Row_Name.END_PAGE] = pages[1]
    #                     try:
    #                         info[Row_Name.PAGE_TOTAL] = int(pages[1]) - int(pages[0]) + 1
    #                     except:
    #                         pass
    #
    #
    #         elif style == "line-height: 14.8pt; margin-top: 0pt; margin-bottom: 0pt;":
    #             if s == 1:
    #                 s = 0
    #             line = p.get_text().replace("\n", " ")
    #             if "ABSTRACT" in line:
    #                 abstract = True
    #             if abstract:
    #                 info[Row_Name.ABSTRACT] = line
    #             if "Key words" in line:
    #                 info[Row_Name.KEYWORD] = line.replace(",", "##")









