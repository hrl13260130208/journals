
import redis
import json




REDIS_IP="10.3.1.99"
REDIS_PORT="6379"
# REDIS_DB="2" #生成使用
REDIS_DB="10" #测试使用



redis_ = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
class name_manager:
    def create_website_journal_set_name(self,website):
        '''
        创建网站下存储期刊名与url的set的名称
        :param website:
        :return:
        '''
        return website+"_journals_set"





    def create_journal_common_info_name(self,journal):
        '''
        创建存储期刊公共信息的string的名称
        :param journal:
        :return:
        '''
        return  journal+"_common_info"

    def create_download_schedule_name(self,journal):
        '''
        创建记录下载进度的set的名称
        :param journal:
        :return:
        '''
        return journal+"_download_schedule_set"

    def create_journal_temp_data_name(self,journal):
        '''
        创建存储期刊卷期层信息的list的名称
        :param journal:
        :return:
        '''
        return  journal+"_temp_data"

    def create_article_data_name(self):
        return  "article_data_list"

    def create_journal_error_message_name(self):
        return  "journal_error_massage_list"

    def create_article_error_message_name(self):
        return  "article_error_massage_list"





    def seve_website_journal_set(self,website,string):
        '''
        存储网站内期刊（期刊名和url）的set
        :param website:
        :param string:
        :return:
        '''
        redis_.sadd(self.create_website_journal_set_name(website),string)

    def smembers_wbsite_journal_set(self,website):
        return redis_.smembers(self.create_website_journal_set_name(website))






    def save_journal_common_info(self,journal,info):
        '''
        存储期刊公共信息
        :param journal:
        :param info:
        :return:
        '''
        redis_.set(self.create_journal_common_info_name(journal),info)

    def get_journal_common_info(self,journal):
        return redis_.get(self.create_journal_common_info_name(journal))

    def save_download_schedule(self, journal, volume, issue):
        '''
        存储下载进度,向set中存储数据存储成功则为增量
        :param journal:
        :param volume:
        :param issue:
        :return:
        '''
        return  redis_.sadd(self.create_download_schedule_name(journal), volume + "_" + issue)

    def smembers_journal_download_schedule(self, journal):
        return redis_.smembers(self.create_download_schedule_name(journal))

    def save_journal_temp_data(self,journal,data):
        redis_.lpush(self.create_journal_temp_data_name(journal),data)

    def get_journal_temp_data(self,journal):
        return redis_.rpop(self.create_journal_temp_data_name(journal))


    def is_increment(self,journal,year,volume,issue):
        '''
        判断期刊是否是增量
        :param journal:
        :param volume:
        :param issue:
        :return:
        '''
        p_year=2018

        if int(year)>=p_year:
            return not redis_.sismember(self.create_download_schedule_name(journal), volume + "_" + issue)
        #     num=self.seve_download_schedule(journal,volume,issue)
        #     return num ==1
        # return False

    def save_article_data(self,data):
        redis_.lpush(self.create_article_data_name(),data)

    def get_article_data(self):
        return redis_.lpop(self.create_article_data_name())

    def save_journal_error_message(self,message):
        redis_.lpush(self.create_journal_error_message_name(),message)

    def save_article_error_message(self,message):
        redis_.lpush(self.create_article_error_message_name(),message)

    def get_journal_error_massage(self):
        return redis_.lpop(self.create_journal_error_message_name())

    def get_article_error_massage(self):
        return redis_.lpop(self.create_article_error_message_name())


def website_info(website):
    nm=name_manager()
    for journal in nm.smembers_wbsite_journal_set(website):
        journal=json.loads(journal)
        print("期刊名称："+journal[0])
        print("url:",journal[1])
        print("已下载卷期：",nm.smembers_journal_download_schedule(journal[0]))
    # print(redis_.sismember(nm.create_download_schedule_name("Journal of Nanoscience and            Nanotechnology"),"19_1"))


def delte_website(website):
    nm = name_manager()
    for journal in nm.smembers_wbsite_journal_set(website):
        journal = json.loads(journal)
        for i in redis_.keys(journal[0]+"*"):
            redis_.delete(i)
    redis_.delete(nm.create_website_journal_set_name(website))

if __name__ == '__main__':
    for key in redis_.keys("*"):
        redis_.delete(key)
        # print(key ,redis_.type(key))
        if redis_.type(key) == "string":
            print(key,redis_.get(key))
        elif redis_.type(key) == "set":
            print(key," : ",redis_.scard(key)," : ",redis_.smembers(key))
        elif redis_.type(key) =="list":
            print(key ," : ",redis_.llen(key)," : ", redis_.lrange(key,0,100))
    # delte_website("future")

    # website_info("aspbs")


