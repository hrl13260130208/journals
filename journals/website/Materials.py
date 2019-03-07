from journals.common import common_journals,Row_Name,common_article
import time
import random
import requests
from bs4 import BeautifulSoup
import json
import re


class journals(common_journals):

    def get(self,website,journal,url):
        print("=============")
        journal_common_info=self.get_common(journal,url)
        journal_common_info[Row_Name.JOURNAL_TITLE] = journal
        journal_common_info[Row_Name.PUBLISHER]=website
        time.sleep(random.random() * 3)

        data = requests.get(url)
        bs = BeautifulSoup(data.text, "html.parser")

        a_set={}
        table=bs.find("table",width="210")
        for a in table.find_all("a"):
            if not a["href"] in a_set:
                a_set[a["href"]]=1
                url_s="http://www.aspbs.com/"+a["href"]
                print(url_s)
                time.sleep(random.random() * 3)
                data_s = requests.get(url_s)
                bs_s = BeautifulSoup(data_s.text, "html.parser")

                for table_s in bs_s.find_all("table"):
                    if table_s.find("table") == None:
                        tt = table_s.find("tr").find("td").get_text().replace("\n","").replace("\r","")

                        if tt.find("Volume") != -1 and tt.find("Number") != -1:
                            issue_info = dict(journal_common_info)
                            volume = re.search("\d+", re.search("Vol.+\d+", tt).group()).group()
                            no = re.search("\d+", re.search("Number.+\d+", tt).group()).group()
                            year = re.search("\d+", re.search("\(.+\d{4}\)", tt).group()).group()
                            issue_info[Row_Name.YEAR]=year
                            issue_info[Row_Name.VOLUME]=volume
                            issue_info[Row_Name.ISSUE]=no


                            print(issue_info)
                            # if self.nm.is_increment(journal,issue_info[Row_Name.YEAR],issue_info[Row_Name.VOLUME],issue_info[Row_Name.ISSUE]):
                            #     self.nm.save_journal_temp_data(journal,json.dumps(issue_info))

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
                                no = re.search("\d+", re.search("Number.+\d+", b_string).group()).group()

                        if int(volume) == int(journal_temp[Row_Name.VOLUME]) and int(no) == int(journal_temp[Row_Name.ISSUE]):
                            for p in trs[i + 1].find_all("p", class_="sans-12"):
                                article_info = dict(journal_temp)
                                a = p.find("a")
                                if a ==None:
                                    continue
                                article_info[Row_Name.TEMP_AURL]=a["href"]
                                # print(article_info)
                                urls.append(article_info)

                            break
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

if __name__ == '__main__':
    journals().get("aspbs","Materials Express","http://www.aspbs.com/mex.html")
