import requests
from bs4 import BeautifulSoup
import time
import random

def wait():
    time.sleep(random.random() * 4+3)
def sciencej():
    filename="zxD20161121193503212"
    title="Plant Knowledge Journal"
    issn="2200-5390"
    eissn="2200-5404"
    url="http://www.sciencej.com/archive2.html"
    data=requests.get(url)
    soup=BeautifulSoup(data.text,"html.parser")
    div=soup.find("div",class_="art-postcontent art-postcontent-0 clearfix")
    for a in div.find_all("a"):
        new_url=a["href"]

if __name__ == '__main__':
    sciencej()
