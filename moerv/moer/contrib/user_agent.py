# -*- coding: utf-8 -*-

import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from scrapy.conf import settings


class CustomUserAgent(UserAgentMiddleware):

    user_agent_list = settings.attributes['USER_AGENT'].value

    def _user_agent(self, spider):
        if hasattr(spider, 'user_agent'):
            return spider.user_agent
        elif self.user_agent:
            return self.user_agent
        return random.choice(self.user_agent_list)

    def process_request(self, request, spider):
        self.user_agent_list = settings.attributes['USER_AGENT'].value
        user_agent = self._user_agent(spider)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
