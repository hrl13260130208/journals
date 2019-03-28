import xlrd
import openpyxl
import xlwt
import os
import logging
import time
import json
from journals.redis_manager import name_manager
from journals.common import Row_Name
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

def create_and_save_execel(section):
    '''
    创建excel并将数据写入execl
    :param section:
    :return:
    '''
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
    execl = openpyxl.load_workbook("C:/execl/提交/wc_hrl_future_20190309_1_20190309.xlsx")
    sheet = execl.get_sheet_by_name("sheet1")
    # print(sheet.cell(3,Row_Name.COLUME_NUM[Row_Name.AFFILIATION]+1).value)

    for i in sheet.rows:
        em = i[Row_Name.COLUME_NUM[Row_Name.EMAIL]].value
        co = i[Row_Name.COLUME_NUM[Row_Name.CORRESPONDING]].value
        # print(em,co)
        if co != None:
            co = co.replace("*", "").replace("E-mail Address:", "")
        if em != None:
            em = em.replace("E-mail Address", "")
            for e in em.split("##"):
                if e != "$$":
                    co = co.replace(e.strip(), "")
                    co += e
        i[Row_Name.COLUME_NUM[Row_Name.EMAIL]].value = em
        i[Row_Name.COLUME_NUM[Row_Name.CORRESPONDING]].value = co

    execl.save("C:/execl/wc_hrl_future_20190309_1_20190309.xlsx")


if __name__ == '__main__':
    # create_and_save_execel("test")
    # test().test()
    # wb=openpyxl.Workbook()
    # sheet=wb.create_sheet("sheet1",0)
    # sheet.cell(1,1,1)
    # wb.save(EXECEL_PATH+"ts.xlsx")

    pass


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





