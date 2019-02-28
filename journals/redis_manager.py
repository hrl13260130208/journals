
import redis




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

    def create_journal_config_name(self,journal_name):
        '''
        创建获取期刊信息的方法名的sting的名称（针对期刊）
        :param journal_name:
        :return:
        '''
        return  journal_name+"_method_name"

    def create_website_journal_config_set_name(self,website):
        '''
        创建获取期刊信息的方法名的set的名称（针对网站）
        :param website:
        :return:
        '''
        return website+ "_method_set"

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

    def save_journal_config(self,website,journal_name,method_name):
        '''
        存储获取期刊信息的方法名
        :param website:
        :param journal_name:
        :param method_name:
        :return:
        '''
        redis_.sadd(self.create_website_journal_config_set_name(website),method_name)
        redis_.set(self.create_journal_config_name(journal_name),method_name)

    def get_journal_config(self,journal_name):
        return redis_.get(self.create_journal_config_name(journal_name))


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

    def seve_download_schedule(self, journal, volume, issue):
        '''
        存储下载进度,向set中存储数据存储成功则为增量
        :param journal:
        :param volume:
        :param issue:
        :return:
        '''
        return  redis_.sadd(self.create_download_schedule_name(journal), volume + "_" + issue)

    def get_download_schedule(self, journal):
        return redis_.get(self.create_download_schedule_name(journal))

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
            num=self.seve_download_schedule(journal,volume,issue)
            return num ==1
        return False

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


