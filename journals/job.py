from journals.redis_manager import name_manager
from configparser import ConfigParser
import threading
import json


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
        pyfile = __import__("journals.website." + self.section, fromlist=True)
        c = getattr(pyfile, "website")
        for item in self.items:
            method=item[0]
            args=item[1].split(";")
            m=getattr(c(),method)
            for arg in args:
                m(self.section,arg)

        for string in self.nm.smembers_wbsite_journal_set(self.section):
            s=json.loads(string)
            print(s[0],s[1])
            print(self.nm.get_journal_config(s[0]))




class jobs:
    def __init__(self):
        self.cofig=configs()

    def run(self):
        thread=[]
        for section in self.cofig.read_sections():
            items=self.cofig.read_items(section)
            s=spider(section,items)
            thread.append(s)
            s.start()






if __name__ == '__main__':
   job=jobs()
   job.run()

