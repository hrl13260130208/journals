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
            method_j = self.nm.get_journal_config(s[0])
            m = getattr(c_instance, "run")
            m(self.section, s[0],s[1],method_j)


            logger.info("爬取 "+s[0]+" 文章级别的信息...")

            ca = getattr(pyfile, "article")
            ca_instance=ca()
            m = getattr(ca_instance, "run")
            m( s[0],method_j)

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






if __name__ == '__main__':
   job=jobs()
   job.run_single_website("future")

    # config=configs()
    # for section in config.read_sections():
    #    excel_rw.create_and_save_execel(section)

