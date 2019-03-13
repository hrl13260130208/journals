import logging
from journals.redis_manager import name_manager
import json


logger=logging.getLogger("logger")
class common_website:
    def __init__(self):
        self.nm=name_manager()
        self.list=[]

    def get(self,section,url):
        '''
        从所给的url中爬取所有的期刊，要求爬取期刊名称和期刊内卷期列表的url

        :param section:
        :param url:
        :return:
        '''
        pass

    def run(self,section,url):
        '''
        执行get方法，并将list中的数据存到redis中

        当get方法出错时，退出程序
        :param section:
        :param url:
        :return:
        '''
        try:
            logger.info("解析url:"+url+"...")
            self.get(section,url)
            logger.info("解析完成！")
        except:
            logger.error("网站爬取出错！",exc_info = True)
            exit(0)

        for item in self.list:
            self.nm.seve_website_journal_set(section, json.dumps(item))

    def set_list(self,title,url):
        self.list.append((title,url))


class common_journals:
    def __init__(self):
        self.nm=name_manager()
        self.method = []

    def get(self,website,journal,url):
        '''
        需要子类实现
            实现内容：
                必需项：YEAR、VOLUME、ISSUE
                期刊层可以爬取的信息（）

        :param website:
        :param journal:
        :param url:
        :return:
        '''
        pass

    def run(self,website,journal,url):

        '''
        执行get方法，将需要采集的期刊信息存储到redis中

        当get方法执行出错时，会执行method中配置的其他方法，当所有方法都执行失败的时候，会将错误信息存储到redis中

        :param website:
        :param journal:
        :param url:
        :return:
        '''

        try:
            logger.info("解析url:"+url)
            if not self.nm.is_discontinue_journal(url):
                self.get(website,journal,url)
        except:
            logger.info("爬取"+journal+"失败!", exc_info=True)
            self.nm.save_journal_error_message(website+"_"+journal+"_"+url)



class common_article:
    def __init__(self):
        self.nm = name_manager()
        self.is_break="break"
        self.is_contiune="continue"

    def run(self,journal):
        '''
        执行first与second方法，爬取文章的具体信息

         当get方法执行出错时，会执行method中配置的其他方法（方法名为journals中配置的方法名+_first(或_second)）
        :param journal:
        :param method_j:
        :return:
        '''
        while (True):
            temp_data = self.nm.get_journal_temp_data(journal)
            if temp_data == None:
                break
            journal_temp = json.loads(temp_data)
            ais=self.do_run(journal_temp)

            if ais !=None:
                for info in ais:
                    self.nm.save_article_data(json.dumps(info))

                self.nm.save_download_schedule(journal_temp[Row_Name.JOURNAL_TITLE], journal_temp[Row_Name.VOLUME],
                                               journal_temp[Row_Name.ISSUE])


    def do_run(self,journal_temp):
        '''

        :param journal_temp:
        :return:
        '''
        ais = []
        len=-1
        try:
            m_first = getattr(self, "first")
            m_second = getattr(self, "second")
            logger.info("爬取"+journal_temp[Row_Name.JOURNAL_TITLE]+"文章列表："+journal_temp[Row_Name.TEMP_URL])
            urls = m_first(journal_temp)
            len=urls.__len__()
            for url in urls:
                try:
                    logger.info("爬取"+journal_temp[Row_Name.JOURNAL_TITLE]+"具体文章："+url[Row_Name.TEMP_AURL])
                    ai = m_second(url)
                    ais.append(ai)
                except:
                    logger.error("爬取文章出错：" + url[Row_Name.TEMP_AURL] + " 。错误信息：", exc_info=True)
                    result=""
                    try:
                        logger.info("执行back方法...")
                        result=self.back(url,ais)
                    except:
                        pass
                    if result==self.is_break:
                        break
                    if result==self.is_contiune:
                        continue
                    message = ["second", json.dumps(url)]
                    self.nm.save_article_error_message(json.dumps(message))
        except:
            logger.error("爬取文章列表出错。错误信息：", exc_info=True)
            message = ["first", json.dumps(journal_temp)]
            self.nm.save_article_error_message(json.dumps(message))
        if len!=-1 and len==ais.__len__():
            return ais

    def first(self,temp_data):
        '''

        :param temp_data:
        :return:
        '''
        pass

    def second(self,article_info):
        '''

        :param article_info:
        :return:
        '''
        pass

    def back(self,article_info,ais):
        '''

        :param article_info:
        :param ais:
        :return:
        '''
        pass


class Row_Name:
    FILENAME = "filename"
    EXCELNAME = "excelname"
    SERIAL_NUMBER = "serial_number"
    EDITOR = "editor"
    ERROR_REPORT = "error_report"
    PUBLISHER = "publisher"
    ISSN = "issn"
    EISSN = "eissn"
    JOURNAL_TITLE = "journal_title"
    ORIGINALJID = "originaljid"
    JID = "jid"
    YEAR = "year"
    VOLUME = "volume"
    ISSUE = "issue"
    ATTACH = "attach"
    ISSUE_TOTAL = "issue_total"
    ISSUE_TITLE = "issue_title"
    STRING_COVER_DATE = "string_cover_date"
    ISSUE_HISTORY = "issue_history"
    ARTICLE_ID = "article_id"
    DOI = "doi"
    ARTICLE_SEQ = "article_seq"
    ELOCATION_ID = "elocation_id"
    ARTICLE_TYPE = "article_type"
    TITLE = "title"
    SUBTITLE = "subtitle"
    TRANS_TITLE = "trans_title"
    TRANS_SUBTITLE = "trans_subtitle"
    LANGUAGE = "language"
    LANGUAGE_ALTERNATIVES = "language_alternatives"
    ABSTRACT = "abstract"
    TRANS_ABSTRACT = "trans_abstract"
    KEYWORD = "keyword"
    TRANS_KEYWORD = "trans_keyword"
    KEYWORD_ALTERNATIVES = "keyword_alternatives"
    SUBJECT = "subject"
    CLASSIFICATION = "classification"
    START_PAGE = "start_page"
    END_PAGE = "end_page"
    PAGE_TOTAL = "page_total"
    RANGE_PAGE = "range_page"
    STRING_PUB_DATE = "string_pub_date"
    RECEIVED_DATE = "received_date"
    REVISED_DATE = "revised_date"
    ACCEPTED_DATE = "accepted_date"
    ONLINE_DATE = "online_date"
    COPYRIGHT_STATEMENT = "copyright_statement"
    COPYRIGHT_YEAR = "copyright_year"
    COPYRIGHT_HOLDER = "copyright_holder"
    LICENSE = "license"
    REFERENCE = "reference"
    ABS_URL = "abs_url"
    PAGEURL = "pageurl"
    FULLTEXT_URL = "fulltext_url"
    FULLTEXT_PDF = "fulltext_pdf"
    CORRESPONDING = "corresponding"
    ARTICLE_NOTE = "article_note"
    AWARDS = "awards"
    AUTHOR_NAME = "author_name"
    NAME_ALTERNATIVES = "name_alternatives"
    COLLAB = "collab"
    EMAIL = "email"
    AFFILIATION = "affiliation"
    AFF_ALTERNATIVES = "aff_alternatives"
    AFF_ADDRESS = "aff_address"
    CONTRIB_ADDRESS = "contrib_address"
    BIO = "bio"
    TEMP_URL="temp_url"
    TEMP_AURL="temp_aurl"
    COLUME_NUM={"filename":0,
                "excelname":1,
                "serial_number":2,
                "editor":3,
                "error_report":4,
                "publisher":5,
                "issn":6,
                "eissn":7,
                "journal_title":8,
                "originaljid":9,
                "jid":10,
                "year":11,
                "volume":12,
                "issue":13,
                "attach":14,
                "issue_total":15,
                "issue_title":16,
                "string_cover_date":17,
                "issue_history":18,
                "article_id":19,
                "doi":20,
                "article_seq":21,
                "elocation_id":22,
                "article_type":23,
                "title":24,
                "subtitle":25,
                "trans_title":26,
                "trans_subtitle":27,
                "language":28,
                "language_alternatives":29,
                "abstract":30,
                "trans_abstract":31,
                "keyword":32,
                "trans_keyword":33,
                "keyword_alternatives":34,
                "subject":35,
                "classification":36,
                "start_page":37,
                "end_page":38,
                "page_total":39,
                "range_page":40,
                "string_pub_date":41,
                "received_date":42,
                "revised_date":43,
                "accepted_date":44,
                "online_date":45,
                "copyright_statement":46,
                "copyright_year":47,
                "copyright_holder":48,
                "license":49,
                "reference":50,
                "abs_url":51,
                "pageurl":52,
                "fulltext_url":53,
                "fulltext_pdf":54,
                "corresponding":55,
                "article_note":56,
                "awards":57,
                "author_name":58,
                "name_alternatives":59,
                "collab":60,
                "email":61,
                "affiliation":62,
                "aff_alternatives":63,
                "aff_address":64,
                "contrib_address":65,
                "bio":66
                }









        




