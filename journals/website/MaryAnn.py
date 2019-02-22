import requests
from bs4 import BeautifulSoup
import time
import random
import json
from journals.redis_manager import name_manager


class website:
    def __init__(self):
        self.nm=name_manager()
    def get(self,section,url):
        time.sleep(random.random()*3)
        data=requests.get(url)
        soup=BeautifulSoup(data.text,"html.parser")
        for div_row in soup.find_all("div",class_="row"):
            for div_tag in div_row.find_all("div",class_="col-sm-6 col-md-3 my-2"):
                a=div_tag.find("a")["href"]
                url="https://home.liebertpub.com"+a
                time.sleep(random.random() * 3)
                data2 = requests.get(url)
                bs = BeautifulSoup(data2.text, "html.parser")
                for a in bs.find_all("a", class_="nav-link px-3"):
                    if a.get_text().strip() == "All Issues":
                        issn_url=a["href"]
                journal_title = bs.find("h1", class_="journal-title").get_text().strip()

                str = json.dumps((journal_title, issn_url))
                self.nm.seve_website_issn_set(section,str)




if __name__ == '__main__':
    url="https://home.liebertpub.com//publications/childhood-obesity/384"
    data = requests.get(url)
    data = data.text
    bs = BeautifulSoup(data, "html.parser")
    for a in bs.find_all("a",class_="nav-link px-3"):
        if a.get_text().strip() == "All Issues":
            issn_url=a["href"]

    journal_title=bs.find("h1",class_="journal-title").get_text().strip()


    str=json.dumps((journal_title,issn_url))
    load_json=json.loads(str)
    print(load_json[0],load_json[1])



