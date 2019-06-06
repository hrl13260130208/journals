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

        soup = BeautifulSoup(data.text, "html.parser")
        for a in soup.find_all("a"):
            if "home" in a.get_text().lower():
                continue
            url1 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE/PROCEEDING/" + a["href"]

            info = {Row_Name.TEMP_URL: url1,Row_Name.JOURNAL_TITLE:"iccm13",Row_Name.VOLUME:"1",Row_Name.ISSUE:"1",Row_Name.PUBLISHER:"iccm13"}
            self.nm.save_journal_temp_data(journal,json.dumps(info))


class article(common_article):

    def first(self,journal_temp):
        urls=[]
        wait()
        data_1 = requests.get(journal_temp[Row_Name.TEMP_URL])
        soup = BeautifulSoup(data_1.text, "html.parser")
        for a in soup.find_all("a"):
            url2 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a["href"][2:]
            info=dict(journal_temp)
            info[Row_Name.TEMP_AURL]= url2
            urls.append(info)
        return urls

    def second(self,article_info):
        wait()
        data_2 = requests.get(article_info[Row_Name.TEMP_AURL])
        soup = BeautifulSoup(data_2.text, "html.parser")
        a = soup.find("a")
        print(a)
        if a != None:
            try:
                url_2 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a["href"][2:]
                article_info[Row_Name.FULLTEXT_URL] = url_2
                article_info[Row_Name.ABS_URL] = data_2.url
                article_info[Row_Name.PAGEURL] = data_2.url
            except:
                pass
        text = soup.get_text()
        if "Keywords:" in text:
            article_info[Row_Name.KEYWORD] = text[text.find("Keywords:") + 9:].replace(",", "##").strip()
        article_info[Row_Name.AFFILIATION] = data_2.text
        return article_info




if __name__ == '__main__':
    urls = []
    url="http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE/INDEX/Index-1606.htm"
    article_info={}
    data_2 = requests.get(url)
    soup = BeautifulSoup(data_2.text, "html.parser")
    a = soup.find("a")
    print(a)
    if a != None:
        try:
            url_2 = "http://www.iccm-central.org/Proceedings/ICCM13proceedings/SITE" + a["href"][2:]
            article_info[Row_Name.FULLTEXT_URL] = url_2
            article_info[Row_Name.ABS_URL] = data_2.url
            article_info[Row_Name.PAGEURL] = data_2.url
        except:
            pass
    text = soup.get_text()
    if "Keywords:" in text:
        article_info[Row_Name.KEYWORD] = text[text.find("Keywords:") + 9:].replace(",", "##").strip()
    article_info[Row_Name.AFFILIATION] = data_2.text

    print(article_info)









