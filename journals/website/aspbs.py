import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
from journals.redis_manager import name_manager
from journals.common import Row_Name,common_website,common_journals,common_article
import logging


logger=logging.getLogger("logger")
class website(common_website):

    def get(self,section,url):

        time.sleep(random.random() * 3)
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "html.parser")
        td = soup.find("td", width="155")
        div = td.find("div")
        for a in div.find_all("a"):
            url = "http://www.aspbs.com/" + a["href"]
            title = a.get_text().strip().replace("\n", " ").replace("\r", " ")

            self.set_list(title, url)

class journals(common_journals):

    def get(self,website,journal,url):
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER]=website
        time.sleep(random.random() * 3)
        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", class_="loi tab loi-tab-2")
        ul = div.find("ul", class_="rlist tab__content")
        for li in ul.find_all("li", class_="col-md-4"):
            issue_info = dict(journal_common_info)

            cdate = li.find("span", class_="coverDate").get_text().strip()
            issue_info[Row_Name.STRING_COVER_DATE] = cdate
            issue_info[Row_Name.YEAR] = cdate[-4:]
            for a in li.find_all("a"):
                a_text = a.get_text().strip()
                vol_num = a_text.find("Vol")
                if vol_num != -1:
                    issue_num = a_text.find("Issue")
                    issue_info[Row_Name.VOLUME] = a_text[vol_num + 4:issue_num].strip()
                    issue_info[Row_Name.ISSUE] = a_text[issue_num + 6:].strip()
                    issue_info[Row_Name.TEMP_URL]="https://www.liebertpub.com"+a["href"]

            if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        info={}
        common=self.nm.get_journal_common_info(journal)

        if common ==None:
            data = requests.get(url)
            bs = BeautifulSoup(data.text, "html.parser")
            div = bs.find("div", class_="text-minute margin-bottom--small")
            div_str = div.get_text().strip()
            for s in div_str.split("|"):
                if s.find("Online ISSN:") != -1:
                    info[Row_Name.EISSN] = s[13:].strip()
                elif s.find("ISSN:") != -1:
                    info[Row_Name.ISSN] = s[5:].strip()

            if Row_Name.ISSN not in info and Row_Name.EISSN not in info:
                raise ValueError("issn与eissn为空！")
            self.nm.save_journal_common_info(journal,json.dumps(info))
            return info
        else:
            return json.loads(common)

if __name__ == '__main__':
    url="http://www.aspbs.com/apm.htm"
    data = requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")


    # url="http://www.aspbs.com/bottom.htm"
    # time.sleep(random.random() * 3)
    # data = requests.get(url)
    # soup = BeautifulSoup(data.text, "html.parser")
    # td=soup.find("td",width="155")
    # div=td.find("div")
    # for a in div.find_all("a"):
    #     url="http://www.aspbs.com/"+a["href"]

        # title=a.get_text().strip().replace("\n"," ").replace("\r"," "))

            # print(a.get_text().strip().replace("\n"," ").replace("\r"," "))



#
#
# class article(common_article):
#
#     def first(self,temp_data):
#         urls=[]
#         journal_temp = json.loads(temp_data)
#         time.sleep(random.random() * 3)
#         data = requests.get(journal_temp[Row_Name.TEMP_URL])
#         bs = BeautifulSoup(data.text, "html.parser")
#
#         div = bs.find("div", class_="table-of-content")
#         for i in div.find_all("div", class_="issue-item"):
#             article_info = dict(journal_temp)
#             # i=div.find("div",class_="issue-item")
#             title = i.find("h5")
#             article_url = title.find("a")["href"]
#             article_info[Row_Name.TEMP_AURL]="https://www.liebertpub.com" + article_url
#
#             article_start_page = i.find("ul", class_="rlist--inline separator toc-item__detail")
#             for li in article_start_page.find_all("li"):
#                 if li.get_text().find("Pages:") != -1:
#                     [s.extract() for s in li.find("span")]
#                     strs = li.get_text().split("–")
#                     try:
#                         article_info[Row_Name.START_PAGE] = int(strs[0])
#                         article_info[Row_Name.END_PAGE] = int(strs[1])
#                         article_info[Row_Name.PAGE_TOTAL] = article_info[Row_Name.END_PAGE] - article_info[
#                             Row_Name.START_PAGE] + 1
#                     except:
#                         article_info[Row_Name.START_PAGE] = strs[0]
#                         article_info[Row_Name.END_PAGE] = strs[1]
#
#                 elif li.get_text().find("Published Online:") != -1:
#                     [s.extract() for s in li.find("span")]
#                     self.set_possible_none_item(article_info, Row_Name.STRING_PUB_DATE, li)
#
#             urls.append(article_info)
#         return urls
#
#     def second(self,article_info):
#
#         time.sleep(random.random() * 3)
#         data_s = requests.get(article_info[Row_Name.TEMP_AURL])
#         bs_c = BeautifulSoup(data_s.text, "html.parser")
#
#         article_type = bs_c.find("meta", {"name": "dc.Type"})
#         self.set_not_none_item(article_info, Row_Name.ARTICLE_TYPE, article_type["content"])
#
#         article_doi = bs_c.find("meta", {"scheme": "doi"})
#         self.set_not_none_item(article_info, Row_Name.DOI, article_doi["content"])
#
#         article_title = bs_c.find("meta", {"name": "dc.Title"})
#         self.set_not_none_item(article_info, Row_Name.TITLE, article_title["content"])
#
#         article_language = bs_c.find("meta", {"name": "dc.Language"})
#         self.set_not_none_item(article_info, Row_Name.LANGUAGE, article_language["content"])
#
#         article_abstract = bs_c.find("div", class_="abstractSection abstractInFull")
#         self.set_possible_none_item(article_info, Row_Name.ABSTRACT, article_abstract)
#
#         article_keyword = bs_c.find("meta", {"name": "keywords"})
#         # self.set_possible_none_item(article_info,Row_Name.KEYWORD,article_keyword["content"].replace(",","##"))
#         if article_keyword != None:
#             article_info[Row_Name.KEYWORD] = article_keyword["content"].replace(",", "##")
#
#
#         for section in bs_c.find_all("section", class_="section"):
#             if section.find("strong").get_text() == "Information":
#                 string = section.find("div").get_text().strip()
#                 article_info[Row_Name.COPYRIGHT_STATEMENT] = string
#                 re_s = re.search("[0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3}", string)
#                 if re_s != None:
#                     article_info[Row_Name.COPYRIGHT_YEAR] = string[re_s.span()[0]:re_s.span()[1]]
#                 if string.find("Mary Ann") != -1:
#                     article_info[Row_Name.COPYRIGHT_HOLDER] = "Mary Ann Liebert, Inc"
#
#         self.set_not_none_item(article_info, Row_Name.ABS_URL, data_s.url)
#         self.set_not_none_item(article_info, Row_Name.FULLTEXT_URL, data_s.url)
#
#         an_string = ""
#         em_string = ""
#         af_string = ""
#         aa_string = ""
#         co_string = ""
#         has_em = False
#         div_a = bs_c.find("div", class_="accordion-tabbed loa-accordion")
#         for div_tag in div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed "}) \
#                        + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile "}):
#             a = div_tag.find("a", href="#")
#             an_string += a["title"].strip() + "##"
#             div_s = div_tag.find("div", class_="author-info accordion-tabbed__content")
#             [s.extract() for s in div_s.find("div", class_="bottom-info")]
#             af = ""
#             aa = ""
#             em = "$$"
#
#             for p in div_s.find_all("p"):
#                 p = p.get_text().strip().replace("\n", " ").replace("\r", " ")
#                 if p.find("Address correspondence to:") != -1:
#                     co_string += p
#                 elif p.find("E-mail Address:") != -1:
#                     has_em = True
#                     em = p.split(":")[1].strip()
#                     co_string += p
#                 elif p != "":
#                     ps = p.split(",")
#                     for i in range(ps.__len__() - 2):
#                         af += ps[i] + ","
#                     af += af[:-1] + ";"
#                     aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
#             em_string += em + "##"
#             af_string += af[:-1] + "##"
#             aa_string += aa[:-1] + "##"
#
#         article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
#         if has_em:
#             article_info[Row_Name.EMAIL] = em_string[:-2]
#         article_info[Row_Name.AFFILIATION] = af_string[:-2]
#         article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]
#         article_info[Row_Name.CORRESPONDING] = co_string[:-2]
#
#         self.nm.save_article_data(json.dumps(article_info))
#
#
#     def get(self,journal):
#         while(True):
#             temp_data=self.nm.get_journal_temp_data(journal)
#             if temp_data ==None:
#                 break
#             journal_temp=json.loads(temp_data)
#             time.sleep(random.random() * 3)
#             data = requests.get(journal_temp[Row_Name.TEMP_URL])
#             bs = BeautifulSoup(data.text, "html.parser")
#
#
#             div = bs.find("div", class_="table-of-content")
#             for i in div.find_all("div", class_="issue-item"):
#                 article_info = dict(journal_temp)
#                 # i=div.find("div",class_="issue-item")
#                 title = i.find("h5")
#                 article_url = title.find("a")["href"]
#
#                 time.sleep(random.random() * 3)
#                 data_s = requests.get("https://www.liebertpub.com" + article_url)
#                 bs_c = BeautifulSoup(data_s.text, "html.parser")
#
#                 article_type = bs_c.find("meta", {"name": "dc.Type"})
#                 self.set_not_none_item(article_info,Row_Name.ARTICLE_TYPE,article_type["content"])
#
#                 article_doi = bs_c.find("meta", {"scheme": "doi"})
#                 self.set_not_none_item(article_info,Row_Name.DOI,article_doi["content"])
#
#                 article_title = bs_c.find("meta", {"name": "dc.Title"})
#                 self.set_not_none_item(article_info,Row_Name.TITLE,article_title["content"])
#
#                 article_language = bs_c.find("meta", {"name": "dc.Language"})
#                 self.set_not_none_item(article_info,Row_Name.LANGUAGE, article_language["content"])
#
#                 article_abstract = bs_c.find("div", class_="abstractSection abstractInFull")
#                 self.set_possible_none_item(article_info,Row_Name.ABSTRACT,article_abstract)
#
#                 article_keyword= bs_c.find("meta", {"name": "keywords"})
#                 # self.set_possible_none_item(article_info,Row_Name.KEYWORD,article_keyword["content"].replace(",","##"))
#                 if article_keyword!=None:
#                     article_info[Row_Name.KEYWORD]= article_keyword["content"].replace(",", "##")
#
#                 article_start_page=i.find("ul",class_="rlist--inline separator toc-item__detail")
#                 for li in article_start_page.find_all("li"):
#                     if li.get_text().find("Pages:")!=-1:
#                         [s.extract() for s in li.find("span")]
#                         strs =li.get_text().split("–")
#                         try:
#                             article_info[Row_Name.START_PAGE]=int(strs[0])
#                             article_info[Row_Name.END_PAGE]=int(strs[1])
#                             article_info[Row_Name.PAGE_TOTAL]=article_info[Row_Name.END_PAGE]-article_info[Row_Name.START_PAGE]+1
#                         except:
#                             pass
#
#                     elif li.get_text().find("Published Online:")!=-1:
#                         [s.extract() for s in li.find("span")]
#                         self.set_possible_none_item(article_info,Row_Name.STRING_PUB_DATE,li)
#
#                 for section in bs_c.find_all("section",class_="section"):
#                     if section.find("strong").get_text()=="Information":
#                         string=section.find("div").get_text().strip()
#                         article_info[Row_Name.COPYRIGHT_STATEMENT]=string
#                         re_s=re.search("[0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3}",string)
#                         if re_s!= None:
#                             article_info[Row_Name.COPYRIGHT_YEAR]=string[re_s.span()[0]:re_s.span()[1]]
#                         if string.find("Mary Ann")!=-1:
#                             article_info[Row_Name.COPYRIGHT_HOLDER]="Mary Ann Liebert, Inc"
#
#                 self.set_not_none_item(article_info,Row_Name.ABS_URL,data_s.url)
#                 self.set_not_none_item(article_info,Row_Name.FULLTEXT_URL,data_s.url)
#
#
#                 an_string=""
#                 em_string=""
#                 af_string=""
#                 aa_string=""
#                 co_string=""
#                 has_em = False
#                 div_a=bs_c.find("div",class_="accordion-tabbed loa-accordion")
#                 for div_tag in div_a.find_all("div",{"class":"accordion-tabbed__tab-mobile accordion__closed "})\
#                                +div_a.find_all("div",{"class":"accordion-tabbed__tab-mobile "}):
#                     a = div_tag.find("a", href="#")
#                     an_string += a["title"].strip() + "##"
#                     div_s = div_tag.find("div", class_="author-info accordion-tabbed__content")
#                     [s.extract() for s in div_s.find("div",class_="bottom-info")]
#                     af = ""
#                     aa = ""
#                     em = "$$"
#
#                     for p in div_s.find_all("p"):
#                         p = p.get_text().strip().replace("\n", " ").replace("\r"," ")
#                         if p.find("Address correspondence to:") != -1:
#                             co_string += p
#                         elif p.find("E-mail Address:") != -1:
#                             has_em=True
#                             em = p.split(":")[1].strip()
#                             co_string += p
#                         elif p !="":
#                             ps = p.split(",")
#                             for i in range(ps.__len__() - 2):
#                                 af += ps[i] + ","
#                             af += af[:-1] + ";"
#                             aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
#                     em_string += em + "##"
#                     af_string += af[:-1]+ "##"
#                     aa_string += aa[:-1] + "##"
#
#                 article_info[Row_Name.AUTHOR_NAME]=an_string[:-2]
#                 if has_em:
#                     article_info[Row_Name.EMAIL]=em_string[:-2]
#                 article_info[Row_Name.AFFILIATION]=af_string[:-2]
#                 article_info[Row_Name.AFF_ADDRESS]=aa_string[:-2]
#                 article_info[Row_Name.CORRESPONDING]=co_string[:-2]
#
#
#                 self.nm.save_article_data(json.dumps(article_info))
#
#
#
#
#     def set_not_none_item(self,a_info,key,value):
#         if value == None:
#             raise ValueError(key+"的值为空！")
#         a_info[key]=value
#
#     def set_possible_none_item(self,a_info,key,value):
#         if value!=None:
#             a_info[key]=value.get_text().strip()
#
#

