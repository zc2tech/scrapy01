# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from importlib import import_module

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from scrapy01.common.misc import NoneSeleniumRequest
from scrapy01.common.selenium import SeleniumMiddleware, SeleniumRequest


class CustomProxyMiddleware(object):
    def __init__(self, settings):
        self.proxy = settings.get('GLOBAL_PROXY')

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxy 
        # request.headers[“Proxy-Authorization”] = 
        #                   basic_auth_header(“<proxy_user>”, “<proxy_pass>”)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)


class MySeleniumMiddleware(SeleniumMiddleware):
    def __init__(self, proxy,driver_name,driver_executable_path,options_list):
        PROXY = proxy
        if (proxy != None):
            webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
                "httpProxy": PROXY,
                "sslProxy": PROXY,
                "proxyType": "MANUAL",
            }
        if driver_name == "firefox":
            firefox_profile = webdriver.FirefoxProfile()
            firefox_profile.set_preference('permissions.default.image', 2)
            options = Options()
            if options_list != None:
                for argument in options_list:
                    options.add_argument(argument)

            firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
            self.driver = Firefox(executable_path=driver_executable_path,firefox_profile=firefox_profile,options=options)
    
    @classmethod
    def from_crawler(cls, crawler):
        proxy = crawler.settings.get('GLOBAL_PROXY')
        driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
        driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
        options_list = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')
        middleware = cls(
            proxy,
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            options_list = options_list,
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)


        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            try:
                WebDriverWait(self.driver, request.wait_time).until(
                    request.wait_until
                )
            except TimeoutException:
                pass

        if request.screenshot:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )


class Scrapy01SpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
            # SeleniumRequest has his own process, so exclude it.
            if not isinstance(request, NoneSeleniumRequest):
                return None

            self.driver.get(request.url)

            for cookie_name, cookie_value in request.cookies.items():
                self.driver.add_cookie(
                    {
                        'name': cookie_name,
                        'value': cookie_value
                    }
                )

            if request.wait_until:
                WebDriverWait(self.driver, request.wait_time).until(
                    request.wait_until
                )

            if request.screenshot:
                request.meta['screenshot'] = self.driver.get_screenshot_as_png()

            if request.script:
                self.driver.execute_script(request.script)

            body = str.encode(self.driver.page_source)

            # Expose the driver via the "meta" attribute
            request.meta.update({'driver': self.driver})

            return HtmlResponse(
                self.driver.current_url,
                body=body,
                encoding='utf-8',
                request=request
            )

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Scrapy01DownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
