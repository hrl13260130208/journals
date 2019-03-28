from journals.redis_manager import name_manager
from journals import excel_rw
from configparser import ConfigParser
import threading
import json
import logging
from  journals.common import Row_Name



logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

class configs:
    def __init__(self):
        self.path="C:/File/workspace/journals/journals/config.cfg"
        self.conf = ConfigParser()
        self.conf.read(self.path)

    def read_sections(self):
       return  self.conf.sections()

    def read_items(self,section):
        return self.conf.items(section)



class spider(threading.Thread):
    def __init__(self,section,items,update):
        threading.Thread.__init__(self)
        self.section=section
        self.items=items
        self.nm=name_manager()
        self.update=update

    def run(self):

        # 遍历网站所有期刊

        journals=self.nm.smembers_wbsite_journal_set(self.section)
        print(journals.__len__())
        if journals.__len__()==0 or self.update:
            self.update_journals()
            journals = self.nm.smembers_wbsite_journal_set(self.section)

        logger.info("爬取期刊中的具体信息...")
        for string in journals:
            s=json.loads(string)
            pyfile = __import__("journals.website." + self.section, fromlist=True)
            self.run_journal(pyfile,self.section,s[0],s[1])
            self.run_article(pyfile,s[0])

    def update_journals(self):
        logger.info("爬取 " + self.section + " 中的所有的期刊...")
        pyfile = __import__("journals.website." + self.section, fromlist=True)
        c = getattr(pyfile, "website")
        for item in self.items:
            args = item[1].split(";")
            m = getattr(c(), "run")
            for arg in args:
                m(self.section, arg)


    def run_journal(self,pyfile,website,journal,url):
        '''
        爬取期刊信息，使用反射执行对应网站的python文件的journals的run方法
        :param pyfile: python文件名
        :param website:
        :param journal:
        :param url:
        :return:
        '''
        logger.info("爬取 " + journal + " 期刊级别的信息...")
        c = getattr(pyfile, "journals")
        c_instance = c()
        m = getattr(c_instance, "run")
        m(website, journal,url)

    def run_article(self,pyfile,journal):
        '''
        爬取文章信息，使用反射执行对应网站的python文件的article的run方法
        :param pyfile:
        :param journal:
        :return:
        '''

        logger.info("爬取 " + journal+ " 文章级别的信息...")
        ca = getattr(pyfile, "article")
        ca_instance = ca()
        m = getattr(ca_instance, "run")
        m(journal)

class jobs:
    def __init__(self):
        self.cofig=configs()

    def run(self,update=False):
        '''
        爬取conf中配置的所有网站
        :return:
        '''
        thread=[]
        pubs={}
        # for section in self.cofig.read_sections():
        #     excel_rw.create_and_save_execel(section)
        logger.info("读取配置文件...")
        for section in self.cofig.read_sections():
            if section=="single":
                for item in self.cofig.read_items(section):
                    pubs=self.run_single_journal(item)
            else:
                if not section in pubs:
                    pubs[section]=1
                items=self.cofig.read_items(section)
                s=spider(section,items,update)
                thread.append(s)
                s.start()
        for t in thread:
            t.join()
        print("===============",pubs)
        write_data(pubs)

    def run_single_website(self, website):
        '''
        爬取指定网站
        :param website:
        :return:
        '''
        pubs = {}
        if website == "single":
            for item in self.cofig.read_items(website):
                pubs = self.run_single_journal(item)
        else:
            pubs[website] = 1
            items = self.cofig.read_items(website)
            s = spider(website, items,False)
            s.start()
            s.join()
        write_data(pubs)

    def run_single_journal(self,item):
        '''
        爬取指定的当期刊（在config中single里配置的项目）
        :param item:
        :return:
        '''
        pubs={}
        pyfile = __import__("journals.website." + item[0], fromlist=True)
        spi=spider(None,None,False)
        for i in item[1].split(";"):
            strs=i.split("_")
            if not strs[0] in pubs:
                pubs[strs[0]]=1
            spi.run_journal(pyfile,strs[0],strs[1],strs[2])
            spi.run_article(pyfile,strs[1])
        return pubs





def write_data(pubs):
    logger.info("创建并写入execl...")
    for pub_key in pubs.keys():
        excel_rw.create_and_save_execel(pub_key)

    logger.info("生成日志...")
    excel_rw.write_logs()

    logger.info("任务完成。")


def run_article_error_test(file,url):
    '''
    重新执行出错的文章级别链接（测试）
    :param file:
    :param url:
    :return:
    '''
    file=open(file)
    for line in file.readlines():
        if line.find(url)!=-1:
            list=json.loads(line)
            dict = json.loads(list[1])
            # dict = list[1]
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
                if dict[Row_Name.TEMP_AURL] == url:
                    pyfile = __import__("journals.website." + dict[Row_Name.PUBLISHER], fromlist=True)
                    ac = getattr(pyfile, "article")
                    m_second = getattr(ac(), "back")  ####
                    print(m_second(dict))


def run_journal_error_test(file,url):
    '''
     重新执行出错的期刊级别链接（测试）
    :param file:
    :param url:
    :return:
    '''
    file = open(file)
    for line in file.readlines():
        if line.find(url) != -1:
            strs=line.split("_")
            pyfile = __import__("journals.website." + strs[0], fromlist=True)
            ac = getattr(pyfile, "journals")
            m_get=getattr(ac(),"get")
            print(m_get(strs[0],strs[1],strs[2]))
def run_journal(pyname,website,journal,url):
    j_spider = spider(None, None, False)
    pyfile = __import__("journals.website." + pyname, fromlist=True)
    j_spider.run_journal(pyfile, website, journal, url)
    j_spider.run_article(pyfile, journal)

    # pyfile = __import__("journals.website." + strs[0], fromlist=True)
    # ac = getattr(pyfile, "journals")
    # m_get = getattr(ac(), "get")
    # print(m_get(strs[0], strs[1], strs[2]))



def run_journal_error(file):
    '''
    重新执行出错的期刊级别所有链接（运行）
    :param file:
    :return:
    '''
    file = open(file)
    j_spider=spider(None,None,False)
    pubs = {}
    for line in file.readlines():
        strs = line.split("_")
        if not strs[0] in pubs:
            pubs[strs[0]] = 1
        pyfile = __import__("journals.website." + strs[0], fromlist=True)
        j_spider.run_journal(pyfile,strs[0],strs[1],strs[2])
        j_spider.run_article(pyfile,strs[1])

    write_data(pubs)

def run_article_error(file):
    '''
     重新执行出错的文章级别所有链接（运行）
    :param file:
    :return:
    '''
    file = open(file)
    errs={}
    pubs={}
    nm=name_manager()
    for line in file.readlines():
        # line_l=json.loads(line)
        # print(line_l)
        temp=json.loads(json.loads(line)[1])
        new_dict={}
        print(temp)
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
        pub=errs[key][Row_Name.PUBLISHER]
        if not pub in pubs:
            pubs[pub]=1
        pyfile = __import__("journals.website." + pub, fromlist=True)
        ac = getattr(pyfile, "article")
        m_get = getattr(ac(), "do_run")
        ais=m_get(errs[key])

        m_save=getattr(ac(),"save_data")
        m_save(ais,errs[key])

    write_data(pubs)



def set_discontinue_journal(url):
    '''
    存储不需要爬取期刊链接
    :param url:
    :return:
    '''
    name_manager().save_discontiune_journal(url)

if __name__ == '__main__':
    # pass

    website="MaryAnn"
    journal="Videourology™"
    url="https://www.liebertpub.com/loi/vid"
    run_journal(website,website,journal,url)



    # job=jobs()
    # job.run()
    # job.run_single_website("MaryAnn")


   # excel_rw.create_and_save_execel("aspbs")
   #
   #  path="C:/execl/20190312_b/article.txt"
   #  # url="http://www.aspbs.com/science/contents-science2018.htm#241"
   #  # run_article_error_test(path,url)
   #  run_article_error(path)

    # path="C:/execl/20190306/journal.txt"
    # url="http://www.aspbs.com/ctn.html"
    # run_journal_error_test(path,url)
    # config=configs()
    # for item in config.read_items("single"):
    #     print(item)
       # excel_rw.create_and_save_execel(section)


    # url="http://www.aspbs.com/ctn.html"
    # print(requests.get("http://www.aspbs.com/ctn.html").text)


