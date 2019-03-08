首先在config中配置需要爬取的网站
    格式：
        [网站名]
        XXX（任意）=期刊列表网址

    特殊项：
        [single]
        python文件名=网站名_期刊名_url连接（多个以;隔开）


运行
    执行job的方法
        爬取config中配置的所有网站：   run
        爬取单个网站                  run_single_website

     爬取过程中会将生成两个错误文件：期刊级别（journal.txt）与文章级别（article.txt）

错误
    非job方法
        重新执行出错的期刊级别链接（测试）         run_journal_error_test （两个参数：错误文件路径、需要重新执行的url）
        重新执行出错的期刊级别所有链接（运行）     run_journal_error       （一个参数：错误文件路径）
        重新执行出错的文章级别链接（测试）         run_article_error_test （两个参数：错误文件路径、需要重新执行的url）
        重新执行出错的文章级别所有链接（运行）     run_article_error       （一个参数：错误文件路径）

查询
    查询爬取期刊的信息的方法在redis_manager中
        查询指定网站下的期刊信息                website_info       （网站名）
        删除指定网站下的所有期刊信息            delete_website     （网站名）
        删除未导出到的数据与错误信息            delete_downloads




