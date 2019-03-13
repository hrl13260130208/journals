import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
from journals.redis_manager import name_manager
from journals.common import Row_Name,common_website,common_journals,common_article
import logging
from journals.job import jobs


logger=logging.getLogger("logger")

def wait():
    time.sleep(random.random() * 5 + 5)
class website(common_website):

    def get(self,section,url):

        wait()
        data = requests.get(url)
        # print(data.text)
        soup = BeautifulSoup(data.text, "html.parser")
        ul = soup.find("ul", class_=" rlist search-result__body titles-results ")

        if ul==None:
            ul=soup.find("ul", class_="rlist search-result__body titles-results")
        num = url.find(".com")
        prefix = url[:num + 4]
        # print("==================",url)
       
        for li in ul.find_all("li"):
            h4 = li.find("h4")
            issn_url = prefix + h4.find("a")["href"]
            journal_title = h4.find("span").get_text().strip()

            self.set_list(journal_title, issn_url)

class journals(common_journals):

    def get(self,website,journal,url):
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER]=website
        wait()
        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        # print(bs)
        num = url.find(".com")
        prefix = url[:num + 4]
        for li in bs.find_all("li", class_="col-md-4"):
            issue_info = dict(journal_common_info)
            # print(li)
            cdate = li.find("span", class_="coverDate").get_text().strip()
            issue_info[Row_Name.STRING_COVER_DATE] = cdate
            issue_info[Row_Name.YEAR] = cdate[-4:]
            for a in li.find_all("a"):
                # print(a)
                a_text = a.get_text().strip()
                vol_num = a_text.find("VOL")
                if vol_num != -1:
                    issue_num = a_text.find("NO")
                    issue_info[Row_Name.VOLUME] = a_text[vol_num + 4:issue_num].strip()
                    issue_info[Row_Name.ISSUE] = a_text[issue_num + 3:].strip()
                    issue_info[Row_Name.TEMP_URL] = prefix + a["href"]
            print(issue_info)
            if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        info={}
        common=self.nm.get_journal_common_info(journal)

        if common ==None:
            wait()
            data = requests.get(url)
            soup = BeautifulSoup(data.text, "html.parser")
            div = soup.find("div", class_="meta__info")
            issn_span = div.find("span", class_="issn")
            eissn_span = div.find("span", class_="eissn")
            if issn_span != None:
                issn = issn_span.get_text().strip()
                info[Row_Name.ISSN] =issn.split(":")[1].strip()

            if eissn_span != None:
                eissn = eissn_span.get_text().strip()
                info[Row_Name.EISSN]=eissn.split(":")[1].strip()

            if Row_Name.ISSN not in info and Row_Name.EISSN not in info:
                raise ValueError("issn与eissn为空！")
            self.nm.save_journal_common_info(journal,json.dumps(info))
            return info
        else:
            return json.loads(common)


class article(common_article):
    def first(self,journal_temp):
        urls=[]
        wait()
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")
        num = journal_temp[Row_Name.TEMP_URL].find(".com")
        prefix = journal_temp[Row_Name.TEMP_URL][:num + 4]
        div = bs.find("div", class_="table-of-content")
        for i in div.find_all("div", class_="issue-item"):
            article_info = dict(journal_temp)
            # i=div.find("div",class_="issue-item")
            title = i.find("h5")
            article_url = title.find("a")["href"]
            article_info[Row_Name.TEMP_AURL]=prefix+ article_url

            article_start_page = i.find("ul", class_="rlist--inline separator toc-item__detail")
            for li in article_start_page.find_all("li"):
                if li.get_text().find("Page") != -1:
                    [s.extract() for s in li.find("span")]
                    strs = li.get_text().split("–")
                    try:
                        article_info[Row_Name.START_PAGE] = int(strs[0])
                        if strs.__len__()<2:
                            article_info[Row_Name.END_PAGE] = int(strs[0])
                        else:
                            article_info[Row_Name.END_PAGE] = int(strs[1])
                        article_info[Row_Name.PAGE_TOTAL] = article_info[Row_Name.END_PAGE] - article_info[
                                Row_Name.START_PAGE] + 1
                    except:
                        article_info[Row_Name.START_PAGE] = strs[0]
                        article_info[Row_Name.END_PAGE] = strs[1]
                        num_0=re.search("\d+",strs[0])
                        num_1=re.search("\d+",strs[1])
                        try:
                            article_info[Row_Name.PAGE_TOTAL]=int(strs[1][num_1.span()[0]:num_1.span()[1]])-int(strs[0][num_0.span()[0]:num_0.span()[1]])
                        except:
                            pass

                elif li.get_text().find("Published Online:") != -1:
                    [s.extract() for s in li.find("span")]
                    self.set_possible_none_item(article_info, Row_Name.STRING_PUB_DATE, li)

            urls.append(article_info)
        return urls

    def second(self,article_info):

        wait()
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs_c = BeautifulSoup(data_s.text, "html.parser")

        article_type = bs_c.find("meta", {"name": "dc.Type"})
        if article_type !=None:
            article_info[ Row_Name.ARTICLE_TYPE]= article_type["content"]

        article_doi = bs_c.find("meta", {"scheme": "doi"})
        if article_doi!=None:
            article_info[ Row_Name.DOI]= article_doi["content"]

        article_title = bs_c.find("meta", {"name": "dc.Title"})
        self.set_not_none_item(article_info, Row_Name.TITLE, article_title["content"])

        article_language = bs_c.find("meta", {"name": "dc.Language"})
        self.set_not_none_item(article_info, Row_Name.LANGUAGE, article_language["content"].lower())

        article_abstract = bs_c.find("div", class_="abstractSection abstractInFull")
        self.set_possible_none_item(article_info, Row_Name.ABSTRACT, article_abstract)

        article_keyword = bs_c.find("meta", {"name": "keywords"})
        # self.set_possible_none_item(article_info,Row_Name.KEYWORD,article_keyword["content"].replace(",","##"))
        if article_keyword != None:
            article_info[Row_Name.KEYWORD] = article_keyword["content"].replace(",", "##")


        for section in bs_c.find_all("section", class_="section"):
            if section.find("strong").get_text() == "Information":
                string = section.find("div").get_text().strip()
                article_info[Row_Name.COPYRIGHT_STATEMENT] = string
                re_s = re.search("[0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3}", string)
                if re_s != None:
                    article_info[Row_Name.COPYRIGHT_YEAR] = string[re_s.span()[0]:re_s.span()[1]]
                    article_info[Row_Name.COPYRIGHT_HOLDER]=string.replace(string[re_s.span()[0]:re_s.span()[1]],"").replace("©","").replace("Copyright","").strip()
                else:
                    article_info[Row_Name.COPYRIGHT_HOLDER] = string.replace("©", "").replace("Copyright", "").strip()


        self.set_not_none_item(article_info, Row_Name.ABS_URL, data_s.url)
        self.set_not_none_item(article_info, Row_Name.FULLTEXT_URL, data_s.url)
        self.set_not_none_item(article_info, Row_Name.PAGEURL, data_s.url)

        an_string = ""
        em_string = ""
        af_string = ""
        aa_string = ""
        co_string = ""
        has_af=False
        has_aa=False
        has_em = False
        div_a = bs_c.find("div", class_="accordion-tabbed loa-accordion")
        #
        name_dict={}
        for div_tag in div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed"}) \
               + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile "})\
                +div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed "}) \
               +div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile"}):
            a = div_tag.find("a", href="#")

            name=a["title"].strip()
            if name in name_dict:
                continue
            name_dict[name]=1
            an_string += name + "##"
            div_s = div_tag.find("div", class_="author-info accordion-tabbed__content")
            [s.extract() for s in div_s.find("div", class_="bottom-info")]
            af = ""
            aa = ""
            em = "$$"

            for p in div_s.find_all("p"):
                p = p.get_text().strip().replace("\n", " ").replace("\r", " ")
                if p.find("Address correspondence to:") != -1:
                    co_string += p
                elif p.find("E-mail Address:") != -1:
                    has_em = True
                    if em.find("$$")!=-1:
                        em = p.split(":")[1].strip()
                    else:
                        em += p.split(":")[1].strip()

                    if co_string.find(em)==-1:
                        co_string += p
                elif p != "":
                    ps = p.split(",")
                    for i in range(ps.__len__() - 2):
                        af += ps[i] + ","
                    af += af[:-1] + ";"
                    aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
            em_string += em + "##"
            if af=="":
                af_string +=  "$$##"
            else:
                af_string += af[:-1] + "##"
                has_af=True

            if aa=="":
                aa_string +=  "$$##"
            else:
                aa_string += aa[:-1] + "##"
                has_aa=True

        article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
        if has_em:
            article_info[Row_Name.EMAIL] = em_string[:-2]
        if has_af:
            article_info[Row_Name.AFFILIATION] = af_string[:-2]
        if has_aa:
            article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]
        article_info[Row_Name.CORRESPONDING] = co_string

        return article_info

    def set_not_none_item(self,a_info,key,value):
        if value == None:
            raise ValueError(key+"的值为空！")
        a_info[key]=value

    def set_possible_none_item(self,a_info,key,value):
        if value!=None:
            a_info[key]=value.get_text().strip()


if __name__ == '__main__':
    # job = jobs()
    # job.run_single_website("future")
    article_info={}
    url="https://www.future-science.com/doi/10.4155/bio-2018-0122"
    data_s = requests.get(url)
    bs_c = BeautifulSoup(data_s.text, "html.parser")

    article_type = bs_c.find("meta", {"name": "dc.Type"})
    if article_type != None:
        article_info[Row_Name.ARTICLE_TYPE] = article_type["content"]

    article_doi = bs_c.find("meta", {"scheme": "doi"})
    if article_doi != None:
        article_info[Row_Name.DOI] = article_doi["content"]



    article_keyword = bs_c.find("meta", {"name": "keywords"})
    # self.set_possible_none_item(article_info,Row_Name.KEYWORD,article_keyword["content"].replace(",","##"))
    if article_keyword != None:
        article_info[Row_Name.KEYWORD] = article_keyword["content"].replace(",", "##")

    for section in bs_c.find_all("section", class_="section"):
        if section.find("strong").get_text() == "Information":
            string = section.find("div").get_text().strip()
            article_info[Row_Name.COPYRIGHT_STATEMENT] = string
            re_s = re.search("[0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3}", string)
            if re_s != None:
                article_info[Row_Name.COPYRIGHT_YEAR] = string[re_s.span()[0]:re_s.span()[1]]
                article_info[Row_Name.COPYRIGHT_HOLDER] = string.replace(string[re_s.span()[0]:re_s.span()[1]],
                                                                         "").replace("©", "").replace("Copyright",
                                                                                                      "").strip()
            else:
                article_info[Row_Name.COPYRIGHT_HOLDER] = string.replace("©", "").replace("Copyright", "").strip()



    an_string = ""
    em_string = ""
    af_string = ""
    aa_string = ""
    co_string = ""
    has_af = False
    has_aa = False
    has_em = False
    div_a = bs_c.find("div", class_="accordion-tabbed loa-accordion")
    #
    name_dict = {}
    for div_tag in div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed"}) \
                   + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile "}) \
                   + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed "}) \
                   + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile"}):
        a = div_tag.find("a", href="#")

        name = a["title"].strip()
        if name in name_dict:
            continue
        name_dict[name] = 1
        an_string += name + "##"
        div_s = div_tag.find("div", class_="author-info accordion-tabbed__content")
        [s.extract() for s in div_s.find("div", class_="bottom-info")]
        af = ""
        aa = ""
        em = "$$"

        for p in div_s.find_all("p"):
            p = p.get_text().strip().replace("\n", " ").replace("\r", " ")
            if p.find("Address correspondence to:") != -1:
                co_string += p
            elif p.find("E-mail Address:") != -1:
                has_em = True
                print("+++++++++++",p)
                if em.find("$$") != -1:

                    print("________________",p.split(":")[1].strip(),p)
                    em = p.split(":")[1].strip()
                else:
                    print("________________", p.split(":")[1].strip())
                    em +=";"+ p.split(":")[1].strip()
                print("===========",em)
                if co_string.find(em) == -1:
                    co_string += p
            elif p != "":
                ps = p.split(",")
                for i in range(ps.__len__() - 2):
                    af += ps[i] + ","
                af += af[:-1] + ";"
                aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
        em_string += em + "##"
        if af == "":
            af_string += "$$##"
        else:
            af_string += af[:-1] + "##"
            has_af = True

        if aa == "":
            aa_string += "$$##"
        else:
            aa_string += aa[:-1] + "##"
            has_aa = True

    article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
    if has_em:
        article_info[Row_Name.EMAIL] = em_string[:-2]
    if has_af:
        article_info[Row_Name.AFFILIATION] = af_string[:-2]
    if has_aa:
        article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]
    article_info[Row_Name.CORRESPONDING] = co_string


    print(article_info)