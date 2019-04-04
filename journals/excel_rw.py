import xlrd
import openpyxl
import xlwt
import os
import logging
import time
import json
from journals.redis_manager import name_manager
from journals.common import Row_Name
import requests
from bs4 import BeautifulSoup
import re



logger = logging.getLogger("logger")

EXECEL_PATH="C:/execl/"

sb={}
def create_colume_name_variable(path):
    '''
    创建表头变量（读取execl表头生成Row_Name中的变量）
    :param path:
    :return:
    '''
    rb = xlrd.open_workbook(path)
    r_sheet = rb.sheet_by_index(0)
    row0=r_sheet.row(0)
    for i in row0:
        print(i.value.upper()+"=\""+i.value+"\"")

def create_and_save_execel(section,*name):
    '''
    创建excel并将数据写入execl
    :param section:
    :return:
    '''

    if name.__len__() != 0:
        execel_name = create_execl_name(name[0])
    else:
        execel_name=create_execl_name(section)
    wb=openpyxl.Workbook()
    sheet=wb.create_sheet("sheet1",0)
    line=2
    write_first_line(sheet)
    while (True):
        article_data = name_manager().get_article_data(section)
        if article_data == None:
            break
        article = json.loads(article_data)
        sheet.cell(line,Row_Name.COLUME_NUM.get(Row_Name.EXCELNAME)+1,execel_name[:-5])
        sheet.cell(line,Row_Name.COLUME_NUM.get(Row_Name.SERIAL_NUMBER)+1,line-1)
        for key in article.keys():
            num=Row_Name.COLUME_NUM.get(key,None)
            if num != None:
                sheet.cell(line,num+1,article[key])

        line+=1

    wb.save(EXECEL_PATH+execel_name)


def create_execl_name(section):
    '''
    创建Excel的名称
    :param section:
    :return:
    '''
    date_time=time.strftime("%Y%m%d", time.localtime())
    return "wc_hrl_"+section+"_"+date_time+"_1_"+date_time+".xlsx"

def write_first_line(sheet):
    d=Row_Name.COLUME_NUM
    for key in d.keys():
        sheet.cell(1,d[key]+1,key)

def write_logs():
    '''
    创建日志
    :return:
    '''
    date_time = time.strftime("%Y%m%d", time.localtime())
    path=EXECEL_PATH+date_time
    if not os.path.exists(path):
        os.mkdir(path)
    journal_name="journal.txt"
    article_name="article.txt"
    write_log(1,path+"/"+journal_name)
    write_log(2,path+"/"+article_name)

def write_log(num,file_path):
    file=open(file_path,"a+",encoding="utf-8")
    nm=name_manager()
    while(True):

        if num ==1:
            temp_data=nm.get_journal_error_massage()
        elif num ==2:
            temp_data=nm.get_article_error_massage()
        if temp_data == None:
            break
        file.write(temp_data+"\n")

def update_excel():
    execl = openpyxl.load_workbook("C:/temp/pages.xlsx")
    sheet = execl.get_sheet_by_name("sheet1")
    # print(sheet.cell(3,Row_Name.COLUME_NUM[Row_Name.AFFILIATION]+1).value)

    for i in sheet.rows:
        url_s = i[Row_Name.COLUME_NUM[Row_Name.ABS_URL]].value
        print(i[Row_Name.COLUME_NUM[Row_Name.START_PAGE]])

        if url_s=="abs_url":
            continue
        data_s = requests.get(url_s)
        bs_c = BeautifulSoup(data_s.text, "html.parser")
        nav = bs_c.find("nav", class_="article__breadcrumbs separator")
        for a in nav.find_all("a"):
            text = a.get_text()
            if "vol" in text.lower() and "no" in text.lower():
                url_f = "https://www.liebertpub.com" + a["href"]
                data = requests.get(url_f)
                bs = BeautifulSoup(data.text, "html.parser")
                prefix = "https://www.liebertpub.com"
                div = bs.find("div", class_="table-of-content")
                for i in div.find_all("div", class_="issue-item"):

                    title = i.find("h5")
                    article_url = title.find("a")["href"]
                    if article_url in url_s:
                        article_start_page = i.find("ul", class_="rlist--inline separator toc-item__detail")
                        for li in article_start_page.find_all("li"):
                            if li.get_text().find("Page") != -1:
                                [s.extract() for s in li.find("span")]
                                strs = li.get_text().split("–")
                                try:
                                    start_p = int(strs[0])
                                    if strs.__len__() < 2:
                                        end_p = int(strs[0])
                                    else:
                                        end_p = int(strs[1])
                                    p_t = end_p - start_p + 1
                                except:
                                    start_p = strs[0]
                                    end_p = strs[1]
                                    num_0 = re.search("\d+", strs[0])
                                    num_1 = re.search("\d+", strs[1])
                                    try:
                                        p_t = int(strs[1][num_1.span()[0]:num_1.span()[1]]) - int(
                                            strs[0][num_0.span()[0]:num_0.span()[1]])
                                    except:
                                        pass
                                print("===============", start_p, end_p, p_t)
                                print(Row_Name.COLUME_NUM[Row_Name.START_PAGE])
                                i[Row_Name.COLUME_NUM[Row_Name.START_PAGE]]=start_p
                                i[Row_Name.COLUME_NUM[Row_Name.END_PAGE]]=end_p
                                i[Row_Name.COLUME_NUM[Row_Name.PAGE_TOTAL]]=p_t

        # if jt.find("  ")!=-1:
        #     i[Row_Name.COLUME_NUM[Row_Name.JOURNAL_TITLE]].value = jt[:jt.find("  ")]
        # try:
        #     # time.sleep(1)
        #     data_s = requests.get(url)
        #     bs_c = BeautifulSoup(data_s.text, "html.parser")
        #     an_string = ""
        #     em_string = ""
        #     af_string = ""
        #     co_string = ""
        #     ans = {}
        #
        #     has_af = False
        #     has_em = False
        #     div_a = bs_c.find("div", class_="accordion-tabbed loa-accordion")
        #     # print(div_a)
        #     for div_tag in div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile accordion__closed"}) \
        #                    + div_a.find_all("div", {"class": "accordion-tabbed__tab-mobile"}):
        #         a = div_tag.find("a", href="#")
        #         if a["title"].strip() in ans:
        #             continue
        #         else:
        #             ans[a["title"].strip()] = 1
        #         an_string += a["title"].strip() + "##"
        #         div_s = div_tag.find("div", class_="author-info accordion-tabbed__content")
        #         [s.extract() for s in div_s.find("div", class_="bottom-info")]
        #         af = ""
        #         aa = ""
        #         em = "$$"
        #         print(div_tag)
        #         print("================", a["title"].strip())
        #         for p in div_s.find_all("p"):
        #             print(p)
        #             [s.extract() for s in p.find_all("p")]
        #             p = p.get_text().strip().replace("\n", " ").replace("\r", " ")
        #
        #             if p.lower().find("correspondence") != -1:
        #                 co_string += p
        #             elif p.find("E-mail Address:") != -1:
        #                 has_em = True
        #                 print(p)
        #                 if em.find("$$") != -1:
        #                     em = p.split(":")[1].strip()
        #                 else:
        #                     em += ";" + p.split(":")[1].strip()
        #                 if p.find(em) == -1:
        #                     co_string += p
        #             elif p != "":
        #                 af += p + ";"
        #                 print("+++++++++++++++", af)
        #         em_string += em + "##"
        #         if af == "":
        #             af_string += "$$##"
        #         else:
        #             af_string += af[:-1] + "##"
        #             has_af = True
        #
        #     i[Row_Name.COLUME_NUM[Row_Name.AUTHOR_NAME]].value = an_string[:-2]
        #     if has_em:
        #         i[Row_Name.COLUME_NUM[Row_Name.EMAIL]].value = em_string[:-2]
        #     if has_af:
        #         i[Row_Name.COLUME_NUM[Row_Name.AFFILIATION]].value = af_string[:-2]
        #
        #         i[Row_Name.COLUME_NUM[Row_Name.CORRESPONDING]].value = co_string
        # except:
        #     pass

        # print(em,co)
        # if co != None:
        #     co = co.replace("*", "").replace("E-mail Address:", "")
        # if em != None:
        #     em = em.replace("E-mail Address", "")
        #     for e in em.split("##"):
        #         if e != "$$":
        #             co = co.replace(e.strip(), "")
        #             co += e
        # i[Row_Name.COLUME_NUM[Row_Name.EMAIL]].value = em
        # i[Row_Name.COLUME_NUM[Row_Name.CORRESPONDING]].value = co

    execl.save("C:/execl/pages.xlsx")


if __name__ == '__main__':

    # url_s="https://www.liebertpub.com/doi/10.1089/jamp.2018.29014.os"
    # data_s = requests.get(url_s)
    # bs_c = BeautifulSoup(data_s.text, "html.parser")
    # nav= bs_c.find("nav",class_="article__breadcrumbs separator")
    # for a in nav.find_all("a"):
    #     text=a.get_text()
    #     if "vol" in text.lower() and "no" in text.lower():
    #         url_f="https://www.liebertpub.com"+a["href"]
    #         data = requests.get(url_f)
    #         bs = BeautifulSoup(data.text, "html.parser")
    #         prefix = "https://www.liebertpub.com"
    #         div = bs.find("div", class_="table-of-content")
    #         for i in div.find_all("div", class_="issue-item"):
    #
    #             title = i.find("h5")
    #             article_url = title.find("a")["href"]
    #             if article_url in url_s:
    #                 article_start_page = i.find("ul", class_="rlist--inline separator toc-item__detail")
    #                 for li in article_start_page.find_all("li"):
    #                     if li.get_text().find("Page") != -1:
    #                         [s.extract() for s in li.find("span")]
    #                         strs = li.get_text().split("–")
    #                         try:
    #                             start_p = int(strs[0])
    #                             if strs.__len__() < 2:
    #                                 end_p= int(strs[0])
    #                             else:
    #                                 end_p = int(strs[1])
    #                             p_t = end_p - start_p + 1
    #                         except:
    #                             start_p = strs[0]
    #                             end_p = strs[1]
    #                             num_0 = re.search("\d+", strs[0])
    #                             num_1 = re.search("\d+", strs[1])
    #                             try:
    #                                 p_t = int(strs[1][num_1.span()[0]:num_1.span()[1]]) - int(
    #                                     strs[0][num_0.span()[0]:num_0.span()[1]])
    #                             except:
    #                                 pass
    #                         print("===============",start_p,end_p,p_t)
    # create_and_save_execel("test")
    # test().test()
    # wb=openpyxl.Workbook()
    # sheet=wb.create_sheet("sheet1",0)
    # sheet.cell(1,1,1)
    # wb.save(EXECEL_PATH+"ts.xlsx")
    update_excel()
    # pass


    #     if pt ==None:
    #         sp=i[Row_Name.COLUME_NUM[Row_Name.START_PAGE]].value
    #         ep=i[Row_Name.COLUME_NUM[Row_Name.END_PAGE]].value
    #
    #         num_0 = re.search("\d+", str(sp))
    #         num_1 = re.search("\d+", str(ep))
    #         try:
    #             num_2 = int(ep[num_1.span()[0]:num_1.span()[1]]) - int(
    #                 sp[num_0.span()[0]:num_0.span()[1]]) + 1
    #             if num_2 > 0:
    #                 i[Row_Name.COLUME_NUM[Row_Name.PAGE_TOTAL]].value = num_2
    #         except:
    #             pass
    #
    #     ch=i[Row_Name.COLUME_NUM[Row_Name.COPYRIGHT_HOLDER]].value
    #
    #     if ch==None:
    #         cs=i[Row_Name.COLUME_NUM[Row_Name.COPYRIGHT_STATEMENT]].value
    #         i[Row_Name.COLUME_NUM[Row_Name.COPYRIGHT_HOLDER]].value=str(cs).replace("©","").replace("Copyright","").strip()

    # execl.save("C:/execl/wc_hrl_MaryAnn_20190228_1_20190208.xlsx")





