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
class website(common_website):

    def get(self,section,url):

        time.sleep(random.random() * 3)
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "html.parser")
        td = soup.find("td", width="155")
        div = td.find("div")
        for a in div.find_all("a"):
            if a["href"].find("http")!=-1:
                url=a["href"]
            else:
                url = "http://www.aspbs.com/" + a["href"]
            title = a.get_text().strip().replace("\n", " ").replace("\r", " ")

            self.set_list(title, url)

class journals(common_journals):

    def get(self,website,journal,url):
        print("=============")
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER]=website
        time.sleep(random.random() * 3)

        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        # print(bs)
        for a in bs.find_all("a"):
            a_string = a.get_text().strip().replace("\n", " ").replace("\r", " ")
            # print(a_string)
            if  a_string.find("Vol") != -1:
                issue_info = dict(journal_common_info)
                issue_info[Row_Name.VOLUME]=re.search("\d+", re.search("Vol.+\d+", a_string).group()).group()
                issue_info[Row_Name.ISSUE] = re.search("\d+/*\d*", re.search("N.+\d+/*\d*", a_string).group()).group()
                cdate=re.search("\(.+\d{4}\)", a_string).group()[1:-1]
                issue_info[Row_Name.STRING_COVER_DATE]=cdate
                issue_info[Row_Name.YEAR]=cdate[-4:]
                issue_info[Row_Name.TEMP_URL] = "http://www.aspbs.com/" + a["href"]

                print(issue_info)
                if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                    self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

    def get_common(self,journal,url):
        info={}
        common=self.nm.get_journal_common_info(journal)

        if common ==None:
            # print(url)
            data = requests.get(url)
            bs = BeautifulSoup(data.text, "html.parser")
            issn_string = ""
            # print(bs)
            for s in bs.find_all("span"):
                string = s.get_text().strip()
                # print(string)
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

    def first(self,journal_temp):

        urls=[]
        print("_____________________")
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
                                no = re.search("\d+/*\d*", re.search("Number.+\d+/*\d*", b_string).group()).group()

                        nos=False

                        if no !=-1:
                            # print(no.find("/") != -1, no, volume)
                            if no.find("/")!=-1:
                                # print("++++++++++++")
                                n=no.split("/")
                                iss=journal_temp[Row_Name.ISSUE].split("/")
                                if int(n[0]) ==int(iss[0]) and int(n[1])==int(iss[1]) :
                                    nos=True
                                    # print("=============")
                                else:
                                    # print("-----------")
                                    continue
                            elif journal_temp[Row_Name.ISSUE].find("/")!=-1:
                                continue
                            else:
                                nos=int(no) == int(journal_temp[Row_Name.ISSUE])

                            if int(volume) == int(journal_temp[Row_Name.VOLUME]) and nos:

                                for p in trs[i + 1].find_all("p", class_="sans-12"):
                                    article_info = dict(journal_temp)
                                    a = p.find_all("a")
                                    if a ==None:
                                        continue
                                    for a_tag in a :
                                        text=a_tag.get_text()
                                        if text.find("Abstract")!=-1 or text.find("Full")!=-1 or text.find("Article]")!=-1:
                                            # print(a_tag["href"]!="v",a_tag["href"])
                                            if a_tag["href"]!="v":
                                                if a_tag["href"].count("http")>1:
                                                    continue
                                                article_info[Row_Name.TEMP_AURL]=a_tag["href"]
                                                break
                                            else:
                                                continue
                                    print(article_info)
                                    urls.append(article_info)

                                break
        return urls

    def back(self,article_info,ais):
        time.sleep(random.random() * 3)
        data_s = requests.get(article_info[Row_Name.TEMP_AURL])
        bs_c = BeautifulSoup(data_s.text, "html.parser")
        urls = []
        ais.clear()
        try:
            div = bs_c.find("div", id="issuesinfo")
            find = False

            for li in div.find_all("li"):
                if li.find("strong") != None:
                    num = re.search("\d+", re.search("Volume.*\d+", li.get_text()).group()).group()
                    if int(num) ==int( article_info[Row_Name.VOLUME]):
                        find = True
                    elif find:
                        break
                if find:
                    a = li.find("a")
                    if a != None:
                        if article_info[Row_Name.ISSUE].find("/")!=-1:
                            if li.get_text().find("-")!=-1:
                                issue_nums = re.findall("\d+", re.search("Numbers.*\d+-\d+",li.get_text()).group())

                                if int(issue_nums[0])== int(article_info[Row_Name.ISSUE].split("/")[0]):
                                    urls = self.do_back_first("https://www.ingentaconnect.com/" + a["href"],
                                                              article_info)
                        else:
                            issue_num = re.search("\d+", re.search("Number.*\d+", li.get_text()).group()).group()

                            if int(issue_num) == int(article_info[Row_Name.ISSUE]):
                                urls=self.do_back_first("https://www.ingentaconnect.com/" + a["href"],article_info)
        except:
            logger.info("没有找到对应的期刊！")
            urls=self.do_back_first(article_info[Row_Name.TEMP_AURL],article_info)


        for url in urls:
            try:
                ai = self.second(url)
                ais.append(ai)
            except:
                logger.error("爬取文章出错：" + url[Row_Name.TEMP_AURL] + " 。错误信息：", exc_info=True)
                message = ["second_back", json.dumps(url)]
                self.nm.save_article_error_message(json.dumps(message))

        return self.is_break



    def do_back_first(self,url,journal_temp):
        urls=[]
        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")
        div = bs.find("div", class_="greybg")
        for div_tag in div.find_all("div", class_="data"):
            a = div_tag.find("a")
            article_info = dict(journal_temp)
            article_info[Row_Name.TEMP_AURL] = "https://www.ingentaconnect.com/"+a["href"]
            print(article_info)
            urls.append(article_info)
        return urls


    def second(self,article_info):
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
        if doi !=None:
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
                        nums = re.findall("\d+", name)
                        af = ""
                        aa = ""

                        if nums.__len__() > 0:
                            has_af = True
                            num = re.search(nums[nums.__len__() - 1], name)
                            name = name[:num.start()]
                            af_aa = author_aff[int(num.group())]
                            ps = af_aa.split(",")
                            if ps.__len__()>2:
                                for i in range(ps.__len__() - 2):
                                    af += ps[i] + ","
                                af += af[:-1] + ";"
                                aa += ps[ps.__len__() - 2] + "," + ps[ps.__len__() - 1] + ";"
                            else:
                                af += af_aa

                        if af == "":
                            af_string += "$$##"
                        else:
                            af_string += af[:-1] + "##"
                        if aa == "":
                            aa_string += "$$##"
                        else:
                            aa_string += aa[:-1] + "##"

                        an_string += name.replace("\xa0", "") + "##"

        article_info[Row_Name.AUTHOR_NAME] = an_string[:-2]
        if has_af:
            article_info[Row_Name.AFFILIATION] = af_string[:-2]
            article_info[Row_Name.AFF_ADDRESS] = aa_string[:-2]

        article_info[Row_Name.ABS_URL] = data_s.url
        article_info[Row_Name.PAGEURL] = data_s.url
        article_info[Row_Name.FULLTEXT_URL] = data_s.url

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
    # job.run_single_website("aspbs")


    url="https://www.ingentaconnect.com/content/asp"
    data=requests.get(url)
    bs = BeautifulSoup(data.text, "html.parser")
    ul=bs.find("ul",class_="bobby")
    for li in ul.find_all("li",class_="journalTitle"):
        a=li.find("a")
        url_s="https://www.ingentaconnect.com"+a["href"]
        print(url_s+"#"+a.get_text().replace("\n",""))


    # article_info={}



