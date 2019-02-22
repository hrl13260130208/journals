
import redis




REDIS_IP="10.3.1.99"
REDIS_PORT="6379"
REDIS_DB="2"


redis_ = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
class name_manager:
    def create_website_journal_set_name(self,website):
        return website+"_journals_set"

    def create_journal_config_name(self,journal_name):
        return  journal_name+"_method_name"

    def create_website_journal_config_set_name(self,website):
        return website+ "_method_set"




    def seve_website_issn_set(self,website,string):
        redis_.sadd(self.create_website_journal_set_name(website),string)

    def smembers_wbsite_issn_set(self,website):
        return redis_.smembers(self.create_website_journal_set_name(website))

    def save_journal_config(self,website,journal_name,method_name):
        redis_.sadd(self.create_website_journal_config_set_name(website),method_name)
        redis_.set(self.create_journal_config_name(journal_name),method_name)

    def get_journal_config(self,journal_name):
        return redis_.get(self.create_journal_config_name(journal_name))


if __name__ == '__main__':
    print(redis_.keys("*"))



