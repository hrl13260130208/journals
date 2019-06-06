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

        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        soup = BeautifulSoup(data.text, "html.parser")
        for font in soup.find_all("font", size="-1"):
            a = font.find("a")
            if a != None:
                url = "http://iccm-central.org/Proceedings/ICCM12proceedings/site/theme/" + a["href"]
                info = {Row_Name.TEMP_URL: url,Row_Name.JOURNAL_TITLE:"iccm12",Row_Name.VOLUME:"1",Row_Name.ISSUE:"1",Row_Name.PUBLISHER:"iccm"}
                self.nm.save_journal_temp_data(journal,json.dumps(info))


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data_1 = requests.get(journal_temp[Row_Name.TEMP_URL])
        soup = BeautifulSoup(data_1.text, "html.parser")
        for a in soup.find_all("a"):
            if "home" in a.get_text().lower() or "back" in a.get_text().lower():
                continue
            url1 = "http://iccm-central.org/Proceedings/ICCM12proceedings/site" + a["href"][2:]
            info=dict(journal_temp)
            info[Row_Name.TEMP_AURL]= url1
            urls.append(info)
        return urls

    def second(self,article_info):
        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        soup = BeautifulSoup(data_s.text, "html.parser")
        p_tags = soup.find_all("p")
        # print(len(p_tags),p_tags)
        font = soup.find("font", size="+1")
        a = font.find("a")
        if a != None:
            url_2 = "http://iccm-central.org/Proceedings/ICCM12proceedings/site" + a["href"][2:]
            article_info[Row_Name.TITLE] = a.get_text()
            article_info[Row_Name.FULLTEXT_URL] = url_2
            article_info[Row_Name.ABS_URL] = data_s.url
            article_info[Row_Name.PAGEURL] = data_s.url

        article_info[Row_Name.AUTHOR_NAME] = str(p_tags[1])
        article_info[Row_Name.AFFILIATION] = str(p_tags[2])
        table = p_tags[3].find("table")
        tds = table.find_all("td")
        if len(tds) == 4:
            if "summary" in tds[0].get_text().lower():
                article_info[Row_Name.ABSTRACT] = tds[1].get_text().strip()
            if "keywords" in tds[2].get_text().lower():
                article_info[Row_Name.KEYWORD] = tds[3].get_text().replace(",", "##").strip()

        print(article_info)

        return article_info




if __name__ == '__main__':
    urls = []
    url="http://iccm-central.org/Proceedings/ICCM12proceedings/site/htmlpap/pap1403.htm"
    article_info={}
    data_s= requests.get(url)
    soup = BeautifulSoup(data_s.text, "html.parser")
    p_tags = soup.find_all("p")
    # print(len(p_tags),p_tags)
    font = soup.find("font", size="+1")
    a = font.find("a")
    if a != None:
        url_2 = "http://iccm-central.org/Proceedings/ICCM12proceedings/site" + a["href"][2:]
        article_info[Row_Name.TITLE] = a.get_text()
        article_info[Row_Name.FULLTEXT_URL] = url_2
        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url

    article_info[Row_Name.AUTHOR_NAME] = p_tags[1]
    article_info[Row_Name.AFFILIATION] = p_tags[2]
    table = p_tags[3].find("table")
    tds = table.find_all("td")
    if len(tds) == 4:
        if "summary" in tds[0].get_text().lower():
            article_info[Row_Name.ABSTRACT] = tds[1].get_text().strip()
        if "keywords" in tds[2].get_text().lower():
            article_info[Row_Name.KEYWORD] = tds[3].get_text().replace(",", "##").strip()

    print(article_info)









