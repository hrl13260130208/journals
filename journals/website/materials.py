from journals.common import common_journals,Row_Name,common_article
import time
import random
import requests
from bs4 import BeautifulSoup
import json
import re
from journals.job import jobs
from journals.website import aspbs


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
                        print(table_s)
                        for tr in table_s.find_all("tr"):
                            tt = tr.find("td").get_text().replace("\n","").replace("\r","")

                            if tt.find("Volume") != -1 and tt.find("Number") != -1:
                                print(tt)
                                issue_info = dict(journal_common_info)
                                volume = re.search("\d+", re.search("Vol.+\d+", tt).group()).group()
                                no = re.search("\d+", re.search("Number.+\d+", tt).group()).group()
                                cdate = re.search("\(.+\d{4}\)", tt).group()
                                year = re.search("\d+",cdate).group()

                                issue_info[Row_Name.YEAR]=year
                                issue_info[Row_Name.VOLUME]=volume
                                issue_info[Row_Name.ISSUE]=no
                                issue_info[Row_Name.TEMP_URL]=url_s
                                issue_info[Row_Name.STRING_COVER_DATE] = cdate[1:-1]
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


class article(aspbs.article):
    pass



if __name__ == '__main__':
    job = jobs()
    job.run_single_website("single")

