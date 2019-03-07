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
            self.run_journal(self.section,s[0],s[1])
            self.run_article(self.section,s[0])




    def run_journal(self,website,journal,url):
        logger.info("爬取 " + journal + " 期刊级别的信息...")

        pyfile = __import__("journals.website." + website, fromlist=True)
        c = getattr(pyfile, "journals")
        c_instance = c()

        m = getattr(c_instance, "run")
        m(website, journal,url)

    def run_article(self,website,journal):
        logger.info("爬取 " + journal+ " 文章级别的信息...")

        pyfile = __import__("journals.website." + website, fromlist=True)
        ca = getattr(pyfile, "article")
        ca_instance = ca()
        m = getattr(ca_instance, "run")
        m(journal)

class jobs:
    def __init__(self):
        self.cofig=configs()

    def run(self):
        thread=[]
        # for section in self.cofig.read_sections():
        #     excel_rw.create_and_save_execel(section)
        logger.info("读取配置文件...")
        for section in self.cofig.read_sections():
            if section=="single":
                items=self.cofig.read_items(section)
                self.run_single_journal()

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


def run_article_error_test(file,url):
    file=open(file)
    for line in file.readlines():
        if line.find(url)!=-1:
            list=json.loads(line)
            dict = json.loads(list[1])
            if list[0] =="first":
                if dict[Row_Name.TEMP_URL] == url:
                    pyfile = __import__("journals.website." + dict[Row_Name.PUBLISHER], fromlist=True)
                    ac=getattr(pyfile,"article")

                    do_run = getattr(ac(), "do_run")
                    print(do_run(json.loads(list[1])))
                    break
            elif list[0] =="second":
                if dict[Row_Name.TEMP_AURL] == url:
                    pyfile = __import__("journals.website." + dict[Row_Name.PUBLISHER], fromlist=True)
                    ac = getattr(pyfile, "article")
                    m_second= getattr(ac(), "second")####
                    print(m_second(dict))
                    break
            elif list[0] =="second_back":
                pass


def run_journal_error_test(file,url):
    file = open(file)
    for line in file.readlines():
        if line.find(url) != -1:
            strs=line.split("_")
            pyfile = __import__("journals.website." + strs[0], fromlist=True)
            ac = getattr(pyfile, "journals")
            m_get=getattr(ac(),"get")
            print(m_get(strs[0],strs[1],strs[2]))


def run_journal_error(file):
    file = open(file)
    j_spider=spider(None,None)
    for line in file.readlines():
        strs = line.split("_")
        j_spider.run_journal(strs[0],strs[1],strs[2])
        j_spider.run_article(strs[0],strs[1])

def run_article_error(file):
    file = open(file)
    errs={}
    nm=name_manager()
    for line in file.readlines():
        temp=json.dumps(json.dumps(line)[1])
        new_dict={}
        if Row_Name.EISSN in temp:
            new_dict[Row_Name.EISSN]=temp[Row_Name.EISSN]
        if Row_Name.ISSN in temp:
            new_dict[Row_Name.ISSN]=temp[Row_Name.ISSN]
        new_dict[Row_Name.JOURNAL_TITLE]=temp[Row_Name.JOURNAL_TITLE]
        new_dict[Row_Name.PUBLISHER]=temp[Row_Name.PUBLISHER]
        new_dict[Row_Name.STRING_COVER_DATE]=temp[Row_Name.STRING_COVER_DATE]
        new_dict[Row_Name.YEAR]=temp[Row_Name.YEAR]
        new_dict[Row_Name.VOLUME]=temp[Row_Name.VOLUME]
        new_dict[Row_Name.ISSUE]=temp[Row_Name.ISSUE]
        new_dict[Row_Name.TEMP_URL]=temp[Row_Name.TEMP_URL]

        string=new_dict[Row_Name.JOURNAL_TITLE]+"_"+new_dict[Row_Name.VOLUME]+"_"+new_dict[Row_Name.ISSUE]

        if not string in errs:
            errs[string]=new_dict

    for key in errs.keys():
        pyfile = __import__("journals.website." + errs[key][Row_Name.PUBLISHER], fromlist=True)
        ac = getattr(pyfile, "article")
        m_get = getattr(ac(), "do_run")
        ais=m_get(errs[key])

        if ais != None:
            for info in ais:
                nm.save_article_data(json.dumps(info))

            nm.save_download_schedule(key[Row_Name.JOURNAL_TITLE], key[Row_Name.VOLUME],
                                           key[Row_Name.ISSUE])

def set_discontinue_journal(url):
    name_manager().save_discontiune_journal(url)

if __name__ == '__main__':
    # job=jobs()
    # job.run_single_website("aspbs")
   # excel_rw.create_and_save_execel("aspbs")

    # path="C:/execl/20190306/article.txt"
    # url="https://www.liebertpub.com/doi/10.1089/lrb.2018.29036.wr"
    # run_article_error_test(path,url)

    # path="C:/execl/20190306/journal.txt"
    # url="http://www.aspbs.com/jbns.html"
    # run_journal_error_test(path,url)
    config=configs()
    for item in config.read_items("single"):
        print(item)
       # excel_rw.create_and_save_execel(section)

