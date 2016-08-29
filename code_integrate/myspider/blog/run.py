#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc :
"""

import logging
from spiders.user_relationship_nets import UserRelationshipNetsSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging


if __name__ == '__main__':
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    runner.crawl(UserRelationshipNetsSpider, 'xrcy168', runner)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
    logging.info('all finished.')
