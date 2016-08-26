#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging, logger

from spiders.moer_spider import MoerSpider

if __name__ == '__main__':
    settings = get_project_settings()
    configure_logging(settings)

    user_set = set()

    runner = CrawlerRunner()
    runner.settings.set(
        'ITEM_PIPELINES', {'moer.pipelines.MoerStorePipeline': 200,
                           'moer.pipelines.ArticleStorePipeline': 300}
    )
    runner.crawl(MoerSpider, runner, user_set)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
    logger.info('All tasks have been finished!')
