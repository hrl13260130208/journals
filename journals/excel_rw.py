import xlrd
import openpyxl
import xlwt
import os
import logging
import time
import json
from journals.redis_manager import name_manager
from journals.common import Row_Name



logger = logging.getLogger("logger")

EXECEL_PATH="C:/execl/"

sb={}
def create_colume_name_variable(path):
    rb = xlrd.open_workbook(path)
    r_sheet = rb.sheet_by_index(0)
    row0=r_sheet.row(0)
    for i in row0:
        print(i.value.upper()+"=\""+i.value+"\"")

def create_and_save_execel(section):
    execel_name=create_execl_name(section)
    wb=openpyxl.Workbook()
    sheet=wb.create_sheet("sheet1",0)
    line=2
    write_first_line(sheet)
    while (True):
        article_data = name_manager().get_article_data()
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
    date_time=time.strftime("%Y%m%d", time.localtime())
    return "wc_hrl_"+section+"_"+date_time+"_1_"+date_time+".xlsx"

def write_first_line(sheet):
    d=Row_Name.COLUME_NUM
    for key in d.keys():
        sheet.cell(1,d[key]+1,key)

def write_logs():
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


class test:
    def test(self):
       try:
           a=1/1

           try:
               b=1/0
           except:
               print("99999999999")
       except:
           print("ssssss")



if __name__ == '__main__':
    # create_and_save_execel("test")
    test().test()
    # wb=openpyxl.Workbook()
    # sheet=wb.create_sheet("sheet1",0)
    # sheet.cell(1,1,1)
    # wb.save(EXECEL_PATH+"ts.xlsx")




    # rb = xlrd.open_workbook("C:/Users/zhaozhijie.CNPIEC/Documents/Tencent Files/2046391563/FileRecv/20190218增量更新/20190218增量更新/wc_vsp_future_20190218_1_20190218.xls")
    # r_sheet = rb.sheet_by_index(0)
    # row0=r_sheet.row(0)
    # for i in row0:
    #     print("\""+i.value+"\":"+str(row0.index(i))+",")



# class excels():
#     def __init__(self,file_path,um):
#         self.file_path=file_path
#         self.um=um
#         self.values=["SOURCENAME","ISSN","EISSN","WAIBUAID","PINJIE","FULL_URL","ABS_URL","FULL_PATH"]
#         self.step=0
#         # self.save_path="C:/pdfs/excel.xls"
#         self.report_path=collect.REPORT_PATH
#         self.write_step=2
#         self.report_step=3
#         self.nums=[]
#         self.create()
#
#     def create(self):
#         rb = xlrd.open_workbook(self.file_path)
#         self.r_sheet = rb.sheet_by_index(0)
#         self.wb = copy.copy(rb)
#         self.w_sheet = self.wb.get_sheet(0)
#         self.init_nums()
#
#     def init_nums(self):
#         self.list = self.r_sheet.row_values(0)
#         for value in self.values:
#             index = self.list.index(value)
#             self.nums.append(index)
#
#     def read(self):
#         logger.info("读取execl...")
#
#         self.create()
#
#         for row in range(self.r_sheet.nrows-1):
#             eb=execl_bean()
#             eb.row_num=row+1
#             eb.sourcename=self.r_sheet.cell(eb.row_num,self.nums[0]).value
#             issn=self.r_sheet.cell(eb.row_num,self.nums[1]).value
#             eissn=self.r_sheet.cell(eb.row_num,self.nums[2]).value
#             if issn =="":
#                 eb.eissn=eissn
#             elif(eissn == ""):
#                 eb.eissn=issn
#             else:
#                 eb.eissn=issn+"-"+eissn
#             eb.waibuaid=self.r_sheet.cell(eb.row_num,self.nums[3]).value
#             eb.pinjie=self.r_sheet.cell(eb.row_num,self.nums[4]).value
#             eb.full_url=self.r_sheet.cell(eb.row_num,self.nums[5]).value
#             eb.abs_url=self.r_sheet.cell(eb.row_num,self.nums[6]).value
#             eb.full_path=self.r_sheet.cell(eb.row_num,self.nums[7]).value
#             if self.list.__len__()> self.nums[7]+1:
#                 page_num=self.r_sheet.cell(eb.row_num,self.nums[7]+1).value
#                 if page_num:
#                     eb.page=int(page_num)
#
#             eb.check()
#
#             if not eb.is_done():
#                 logger.info(eb.to_string())
#                 self.um.save_sourcenames(eb.sourcename)
#                 self.um.save(eb,self.step)
#         logger.info("execl读取完成。")
#
#     def write(self):
#         logger.info("写入execl...")
#         for sn in self.um.get_sourcenames():
#             while (True):
#                 url_name=self.um.fix(sn,self.write_step)
#                 string = self.um.get_eb(url_name)
#                 if string == None:
#                     break
#                 eb = execl_bean()
#                 eb.paser(string)
#
#                 self.w_sheet.write(eb.row_num,self.nums[5],eb.full_url)
#                 self.w_sheet.write(eb.row_num,self.nums[6],eb.abs_url)
#                 self.w_sheet.write(eb.row_num,self.nums[7],eb.full_path)
#                 self.w_sheet.write(eb.row_num,self.nums[7]+1,eb.page)
#
#         self.wb.save(self.file_path)
#         logger.info("Excel写入完成。")
#
#     def report(self):
#         file=open(self.report_path,"a+")
#         for sn in self.um.get_sourcenames():
#             while (True):
#                 url_name=self.um.fix(sn,self.report_step)
#                 string = self.um.get_eb(url_name)
#                 if string == None:
#                     break
#                 file.write(string+"\n")
#
#         logger.info("report文件写入完成。")
#
#
# if __name__ == '__main__':
#     name="dfsf"
#     um = url_manager(name)
#     file_path = "C:/Users/zhaozhijie.CNPIEC/Desktop/temp/中信所待补全文清单_20181219..xls"
#     ex=excels(file_path,um)
#     ex.read()
#     ex.write()
#



