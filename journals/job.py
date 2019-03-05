from journals.redis_manager import name_manager
from journals import excel_rw
from configparser import ConfigParser
import threading
import json
import logging
import openpyxl
from  journals.common import Row_Name


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

class configs:
    def __init__(self):
        self.path="config.cfg"
        self.conf = ConfigParser()
        self.conf.read(self.path)

    def read_sections(self):
       return  self.conf.sections()

    def read_items(self,section):
        return self.conf.items(section)



class spider(threading.Thread):
    def __init__(self,section,items):
        threading.Thread.__init__(self)
        self.section=section
        self.items=items
        self.nm=name_manager()

    def run(self):

        # 遍历网站所有期刊
        logger.info("爬取 "+self.section+" 中的所有的期刊...")
        pyfile = __import__("journals.website." + self.section, fromlist=True)
        c = getattr(pyfile, "website")
        for item in self.items:
            args=item[1].split(";")
            m=getattr(c(),"run")
            for arg in args:
                m(self.section,arg)

        logger.info("爬取期刊中的具体信息...")
        for string in self.nm.smembers_wbsite_journal_set(self.section):
            s=json.loads(string)
            logger.info("爬取 "+s[0]+" 期刊级别的信息...")

            pyfile = __import__("journals.website." + self.section, fromlist=True)
            c = getattr(pyfile, "journals")
            c_instance=c()

            m = getattr(c_instance, "run")
            m(self.section, s[0],s[1])


            logger.info("爬取 "+s[0]+" 文章级别的信息...")

            ca = getattr(pyfile, "article")
            ca_instance=ca()
            m = getattr(ca_instance, "run")
            m( s[0])

class jobs:
    def __init__(self):
        self.cofig=configs()

    def run(self):
        thread=[]
        # for section in self.cofig.read_sections():
        #     excel_rw.create_and_save_execel(section)
        logger.info("读取配置文件...")
        for section in self.cofig.read_sections():
            items=self.cofig.read_items(section)
            s=spider(section,items)
            thread.append(s)
            s.start()
        for t in thread:
            t.join()



        logger.info("创建并写入execl...")
        for section in self.cofig.read_sections():
            excel_rw.create_and_save_execel(section)

        logger.info("生成日志...")
        excel_rw.write_logs()

        logger.info("任务完成。")

    def run_single_website(self,website):
        items = self.cofig.read_items(website)
        s = spider(website, items)
        s.start()
        s.join()
        excel_rw.create_and_save_execel(website)

        logger.info("生成日志...")
        excel_rw.write_logs()

        logger.info("任务完成。")



    def run_file(self,path):
        file=open(path,encoding="utf-8")
        for line in file.readlines():
            message=json.loads(line)
            section=message[1][Row_Name.PUBLISHER]


def run_error_test(file,url):
    file=open(file)
    for line in file.readlines():
        if line.find(url)!=-1:
            list=json.loads(line)
            print(type(list[1])=="str")
            if type(list[1])=="str":
                dict = json.loads(list[1])
            else:
                dict=list[1]
            if list[0] =="first":
                if dict[Row_Name.TEMP_URL] == url:
                    pyfile = __import__("journals.website." + dict[Row_Name.PUBLISHER], fromlist=True)
                    ac=getattr(pyfile,"article")

                    do_run = getattr(ac(), "do_run")
                    print(do_run(json.loads(list[1])))
                    break
            elif list[0] =="second":
                if list[0] == "second":
                    if dict[Row_Name.TEMP_AURL] == url:
                        pyfile = __import__("journals.website." + dict[Row_Name.PUBLISHER], fromlist=True)
                        ac = getattr(pyfile, "article")

                        m_second= getattr(ac(), "second")####

                        m_second(dict)

                        break









if __name__ == '__main__':
    job=jobs()
    job.run_single_website("aspbs")
   # excel_rw.create_and_save_execel("aspbs")

    # path="C:/execl/20190305/article.txt"
    # url="http://openurl.ingenta.com/content?genre=article&issn=1941-4900&volume=10&issue=5/6&spage=603&epage=605"
    # run_error_test(path,url)
    # config=configs()
    # for section in config.read_sections():
    #    excel_rw.create_and_save_execel(section)

