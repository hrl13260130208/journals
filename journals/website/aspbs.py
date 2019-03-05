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
        for a in bs.find_all("a"):
            a_string = a.get_text().strip().replace("\n", " ").replace("\r", " ")
            # print(a_string)
            if  a_string.find("Vol") != -1:
                issue_info = dict(journal_common_info)
                issue_info[Row_Name.VOLUME]=re.search("\d+", re.search("Vol.+\d+", a_string).group()).group()
                issue_info[Row_Name.ISSUE]=re.search("\d+", re.search("N.+\d+", a_string).group()).group()
                cdate=re.search("\(.+\d{4}\)", a_string).group()[1:-1]
                issue_info[Row_Name.STRING_COVER_DATE]=cdate
                issue_info[Row_Name.YEAR]=cdate[-4:]
                issue_info[Row_Name.TEMP_URL] = "http://www.aspbs.com/" + a["href"]

                if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                    self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        info={}
        common=self.nm.get_journal_common_info(journal)

        if common ==None:
            data = requests.get(url)
            bs = BeautifulSoup(data.text, "html.parser")
            issn_string = ""
            for s in bs.find_all("span"):
                string = s.get_text().strip()
                if string.find("ISSN") != -1 or string.find("EISSN") != -1:
                    issn_string = string
                    break
            if issn_string == "":
                for f in bs.find_all("font"):
                    string1 = f.get_text().strip()
                    if string1.find("ISSN") != -1 or string1.find("EISSN") != -1:
                        issn_string = string1
                        break

            if issn_string == "":
                try:
                    eissn_s = re.search("EISSN.* .{4}-.{4}", bs.get_text()).group()
                    issn_s = re.search("ISSN.* .{4}-.{4}", bs.get_text()).group()
                except:
                    eissn_s = re.search("ISSN.* .{4}-.{4}.*(Online) ", bs.get_text()).group()
                    eissn_s="E"+eissn_s
                    issn_s = re.search("ISSN.* .{4}-.{4}.*(Print)", bs.get_text()).group()
                if eissn_s != None:
                    issn_string += eissn_s + ";"

                if issn_s != None:
                    issn_string += issn_s + ";"

            if issn_string != "":
                iss = issn_string.split(";")
                for issn in iss:
                    if issn.find("EISSN") != -1:
                        info[Row_Name.EISSN] = re.search(".{4}-.{4}", issn).group()
                    elif issn.find("ISSN") != -1:
                        info[Row_Name.ISSN] = re.search(".{4}-.{4}", issn).group()

            if Row_Name.ISSN not in info and Row_Name.EISSN not in info:
                raise ValueError("issn与eissn为空！")
            self.nm.save_journal_common_info(journal,json.dumps(info))
            return info
        else:
            return json.loads(common)

class article(common_article):

    def first(self,temp_data):
        print("==========================")
        urls=[]
        journal_temp = json.loads(temp_data)
        time.sleep(random.random() * 3)
        data = requests.get(journal_temp[Row_Name.TEMP_URL])
        bs = BeautifulSoup(data.text, "html.parser")

        for table in bs.find_all("table"):
            if table.find("table") == None:
                tt = table.find("tr").find("td").get_text()
                if tt.find("Volume") != -1 and tt.find("Number") != -1:
                    trs = table.find_all("tr")
                    for i in range(trs.__len__()):
                        volume = -1
                        no = -1
                        for b in trs[i].find_all("b"):
                            b_string = b.get_text().strip().replace("\n", " ").replace("\r", " ")
                            if b_string.find("Volume") != -1 and b_string.find("Number") != -1:
                                volume = re.search("\d+", re.search("Vol.+\d+", b_string).group()).group()
                                no = re.search("\d+", re.search("Number.+\d+", b_string).group()).group()
                        print(volume,no,"===========",journal_temp[Row_Name.VOLUME],journal_temp[Row_Name.ISSUE])
                        if int(volume) == int(journal_temp[Row_Name.VOLUME]) and int(no) == int(journal_temp[Row_Name.ISSUE]):
                            for p in trs[i + 1].find_all("p", class_="sans-12"):
                                article_info = dict(journal_temp)
                                a = p.find("a")
                                article_info[Row_Name.TEMP_AURL]=a["href"]
                                print(article_info)
                                urls.append(article_info)

                            break

        return urls

    def second(self,article_info):
        print("______________________")
        time.sleep(random.random() * 3)
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs_c = BeautifulSoup(data_s.text, "html.parser")

        div_1 = bs_c.find("div", {"id": "Info"})
        author_aff = {}
        an_string = ""
        af_string = ""
        aa_string = ""
        has_af = False
        for p in div_1.find_all("p"):
            string_p = p.get_text().strip().replace("\n", " ").replace("\r", " ")
            if string_p.find("Keywords:") != -1:
                article_info[Row_Name.KEYWORD] = string_p.split(":")[1].replace(";", "##")
            elif string_p.find("Document Type:") != -1:
                article_info[Row_Name.ARTICLE_TYPE] = string_p.split(":")[1]
            elif string_p.find("Publication date:") != -1:
                article_info[Row_Name.STRING_PUB_DATE] = string_p.split(":")[1]
            elif string_p.find("Affiliations:") != -1:
                i = 1
                for span in p.find_all("span"):
                    author_aff[i] = span.get_text()
                    i += 1

        doi = bs_c.find("meta", {"name": "DC.identifier"})
        article_info[Row_Name.DOI] = doi["content"][9:]

        article_title = bs_c.find("meta", {"name": "DC.title"})
        article_info[Row_Name.TITLE] = article_title["content"]

        lang = bs_c.find("html")
        article_info[Row_Name.LANGUAGE] = lang["lang"]

        abs = bs_c.find("div", id="Abst")
        article_info[Row_Name.ABSTRACT] = abs.get_text().strip().replace("\n", " ").replace("\r", " ")

        for div_2 in bs_c.find_all("div", class_="supMetaData"):
            for p1 in div_2.find_all("p"):

                if p1.get_text().find("Source:") != -1:
                    page = p1.find("span", class_="pagesNum").get_text()
                    article_info[Row_Name.START_PAGE] = re.search("\d+-", page).group()[:-1]
                    article_info[Row_Name.END_PAGE] = re.search("-\d+", page).group()[1:]
                    article_info[Row_Name.PAGE_TOTAL] = re.search("\(\d+\)", page).group()[1:-1]

                elif p1.get_text().find("Authors:") != -1:

                    [s.extract() for s in p1.find_all("strong")]
                    for name in p1.get_text().split(";"):
                        num = re.search("\d+", name)
                        af = ""
                        aa = ""

                        if num != None:
                            has_af = True
                            name = name[:num.start()]
                            af_aa = author_aff[int(num.group())]
                            ps = af_aa.split(",")
                            for i in range(ps.__len__() - 2):
                                af += ps[i] + ","
                            af += af[:-1] + ";"
                            aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"

                        if af == "":
                            af_string += "$$##"
                        else:
                            af_string += af[:-1] + "##"
                        if aa == "":
                            aa_string += "$$##"
                        else:
                            aa_string += af[:-1] + "##"

                        an_string += name.replace("\xa0", "") + "##"

        article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
        if has_af:
            article_info[Row_Name.AFFILIATION] = af_string[:-2]
            article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url
        article_info[Row_Name.FULLTEXT_URL] = data_s.url

        print(article_info)
        self.nm.save_article_data(json.dumps(article_info))

    def set_not_none_item(self,a_info,key,value):
        if value == None:
            raise ValueError(key+"的值为空！")
        a_info[key]=value

    def set_possible_none_item(self,a_info,key,value):
        if value!=None:
            a_info[key]=value.get_text().strip()



if __name__ == '__main__':
    info={}
    url="http://www.aspbs.com/jolpe.html"

    data = requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    issn_string = ""
    for s in bs.find_all("span"):
        string = s.get_text().strip()
        if string.find("ISSN") != -1 or string.find("EISSN") != -1:
            issn_string = string
            break
    if issn_string == "":
        for f in bs.find_all("font"):
            string1 = f.get_text().strip()
            if string1.find("ISSN") != -1 or string1.find("EISSN") != -1:
                issn_string = string1
                break

    if issn_string == "":
        eissn_s =re.search("EISSN: \d{4}-\d{4}", bs.get_text()).group()
        if eissn_s!=None:
            issn_string+=eissn_s+";"
        issn_s =re.search("ISSN: \d{4}-\d{4}", bs.get_text()).group()
        if issn_s!=None:
            issn_string+=issn_s+";"

    print(issn_string)
    if issn_string != "":
        iss = issn_string.split(";")
        for issn in iss:
            if issn.find("EISSN:") != -1:
                info[Row_Name.EISSN] = re.search("\d{4}-\d{4}", issn).group()
            elif issn.find("ISSN:") != -1:
                info[Row_Name.ISSN] = re.search("\d{4}-\d{4}", issn).group()
    print(info)
    # data = requests.get(url)
    # bs_c = BeautifulSoup(data.text, "html.parser")
    # article_info={}
    # print(bs_c)
    #
    # div_1=bs_c.find("div",{"id":"Info"})
    # author_aff={}
    # an_string = ""
    # af_string = ""
    # aa_string = ""
    # has_af=False
    # for p in div_1.find_all("p"):
    #     string_p=p.get_text().strip().replace("\n", " ").replace("\r", " ")
    #     if string_p.find("Keywords:")!=-1:
    #         article_info[Row_Name.KEYWORD]=string_p.split(":")[1].replace(";","##")
    #     elif string_p.find("Document Type:")!=-1:
    #         article_info[Row_Name.ARTICLE_TYPE]=string_p.split(":")[1]
    #     elif string_p.find("Publication date:")!=-1:
    #         article_info[Row_Name.STRING_PUB_DATE]=string_p.split(":")[1]
    #     elif string_p.find("Affiliations:")!=-1:
    #         i=1
    #         for span in p.find_all("span"):
    #             author_aff[i]=span.get_text()
    #             i+=1
    #
    #
    # doi=bs_c.find("meta",{"name":"DC.identifier"})
    # article_info[Row_Name.DOI]=doi["content"][9:]
    #
    # article_title = bs_c.find("meta", {"name": "DC.title"})
    # article_info[Row_Name.TITLE]=article_title["content"]
    #
    # lang=bs_c.find("html")
    # article_info[Row_Name.LANGUAGE]=lang["lang"]
    #
    # abs=bs_c.find("div",id="Abst")
    # article_info[Row_Name.ABSTRACT]=abs.get_text().strip().replace("\n", " ").replace("\r", " ")
    #
    # for div_2 in bs_c.find_all("div",class_="supMetaData"):
    #     for p1 in div_2.find_all("p"):
    #
    #         if p1.get_text().find("Source:")!=-1:
    #             page=p1.find("span",class_="pagesNum").get_text()
    #             article_info[Row_Name.START_PAGE]=re.search("\d+-",page).group()[:-1]
    #             article_info[Row_Name.END_PAGE]=re.search("-\d+",page).group()[1:]
    #             article_info[Row_Name.PAGE_TOTAL]=re.search("\(\d+\)",page).group()[1:-1]
    #
    #         elif p1.get_text().find("Authors:")!=-1:
    #
    #
    #             [s.extract() for s in p1.find_all("strong")]
    #             for name in p1.get_text().split(";"):
    #                 num=re.search("\d+",name)
    #                 af=""
    #                 aa=""
    #
    #                 if num !=None:
    #                     has_af=True
    #                     name = name[:num.start()]
    #                     af_aa=author_aff[int(num.group())]
    #                     ps = af_aa.split(",")
    #                     for i in range(ps.__len__() - 2):
    #                         af += ps[i] + ","
    #                     af += af[:-1] + ";"
    #                     aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
    #
    #                 if af == "":
    #                     af_string += "$$##"
    #                 else:
    #                     af_string += af[:-1] + "##"
    #                 if aa == "":
    #                     aa_string += "$$##"
    #                 else:
    #                     aa_string += af[:-1] + "##"
    #
    #                 an_string += name.replace("\xa0", "")+"##"
    #
    # article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
    # if has_af:
    #     article_info[Row_Name.AFFILIATION] = af_string[:-2]
    #     article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]
    #
    # article_info[Row_Name.ABS_URL]=data.url
    # article_info[Row_Name.PAGEURL]=data.url
    # article_info[Row_Name.FULLTEXT_URL]=data.url
    #
    #
    #
    # print(article_info)





    # string="Volume 2, No. 5 (Oct. 2002)"
    # print(re.search("\d+",re.search("Volume \d+",string).group()).group())
    # print(re.search("\d+",re.search("No. \d+",string).group()).group())
    # print(re.search("\(.+\d{4}\)",string).group()[1:-1])




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

#
#

