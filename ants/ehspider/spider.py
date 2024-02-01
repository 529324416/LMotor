from ants.ergate.utils import *
from ants.ergate.spider import *
from ants.ergate.core import *

import re
import bs4
import time

def clear_title(title: str) -> str:
    '''清除标题中的非法字符'''

    return title.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')


class EHApi:
    '''和E站相关的API函数'''

    DEFAULT_PAGE_CAPACITY = 40

    @staticmethod
    def check_url_format(url:str) -> bool:
        '''检查给定的网络链接是否正确'''

        return re.match(r"(http|https)://e\-hentai\.org/g/[0-9]+/[a-z0-9]+(/|)", url)

    @staticmethod
    def is_content_warning(soup: bs4.BeautifulSoup):
        '''检查给定的页面是否是内容警告'''

        titles = soup.find_all('h1')
        for title in titles:
            if title.get_text() == 'Content Warning':
                return True
        return False

    @staticmethod
    def get_total_imagecount(soup: bs4.BeautifulSoup) -> int:
        '''获取所有的图片的数量'''

        try:
            element = soup.find("p", attrs={"class":"gpc"})
            if element == None:
                return -1
            texts = element.text.split("of")
            if len(texts) != 2:
                return -1
            _value = texts[1].replace("images","").replace(",","").replace("，", "").strip()
            return int(_value)
        except:
            return -1

    @staticmethod
    def get_total_pagecount(soup: bs4.BeautifulSoup) -> int:
        '''取得页面总数量'''

        image_count = EHApi.get_total_imagecount(soup)
        if image_count < 0:
            return -1
        if image_count % EHApi.DEFAULT_PAGE_CAPACITY == 0:
            return image_count // EHApi.DEFAULT_PAGE_CAPACITY
        return (image_count // EHApi.DEFAULT_PAGE_CAPACITY) + 1

    @staticmethod
    def get_extra_pages(url:str, soup: bs4.BeautifulSoup) -> list:
        '''获取所有额外的页面链接地址'''

        output = list()
        page_count = EHApi.get_total_pagecount(soup)
        if page_count < 0:
            return output
        url = url.strip("/")
        for i in range(1, page_count):
            output.append(f"{url}/?p={i}")
        return output

    @staticmethod
    def get_images(soup: bs4.BeautifulSoup) -> list:
        '''解析这个页面之下所有图片的链接'''

        divlist = soup.find_all("div", attrs={"class":"gdtm"})
        o = list()
        for div in divlist:
            url = div.find("a").attrs["href"]
            if url != None:
                o.append(url)
        return o

    @staticmethod
    def get_image_src(text: str) -> str:
        '''根据图片页面的文本内容获取图片的真实链接'''

        _soup = bs4.BeautifulSoup(text, "lxml")
        _element = _soup.find('img', attrs={'id':'img'})
        if _element != None:
            return _element.attrs['src']
        return None

    @staticmethod
    def get_title(soup: bs4.BeautifulSoup) -> str:
        '''获取漫画的标题'''

        elem = soup.find("h1", attrs={"id":"gn"})
        if elem != None:
            return elem.text
        return None


class EhSpider:
    '''E站爬虫'''

    def __init__(self, folder, proxies, afterDone:callable, hds = "./bee/ehspider/hds.txt"):
        '''初始化爬虫对象'''

        self.logsystem = Logger(f"{folder}/log.txt")
        self.spider = ConstantSpider(hds)
        self.spider.set_proxies(proxies)
        self.downloader = _ImageDownloader(self.spider, self.logsystem.log, self.record)
        self.fetcher = _ImageFetcher(self.spider, self.downloader, self.logsystem.log, self.record)
        self.folder = folder
        self.afterDone = afterDone
        self._handled_count = 0
        self._total_count = 0
        self._complete_imgs = []

    def record(self, ret, imgpath):
        '''每完成一个图片的下载时就会执行该确定一下是不是所有的图片都下载完成了'''

        self._handled_count += 1
        if ret:
            self._complete_imgs.append(imgpath)
        if self._handled_count >= self._total_count:
            self.afterDone(
                self.title,
                self.folder,
                self._complete_imgs
            )
    
    def say(self, msg:str):
        '''输出信息'''

        self.logsystem.log(msg)

    def _download_main_page(self, url:str, log:callable, retry_times=3) -> bs4.BeautifulSoup:
        '''下载主页面,重试次数为3次'''

        # 启动下载并检查是否是ContentWarning页面
        _cnt = self.spider.get_url(url, show_error=True, target_func=log)
        if _cnt == None:
            if retry_times > 0:
                self.say("主页面下载失败,3秒后准备重试")
                time.sleep(3)
                return self._download_main_page(url, log, retry_times - 1)
            else:
                self.say("重试次数超过,退出下载")
                return None
        else:
            # 下载成功,检测页面是否为警告页面(警告页面不会进行重试)
            soup = bs4.BeautifulSoup(_cnt, "lxml")
            if EHApi.is_content_warning(soup):
                _cnt = self.spider.get_url(url + "?nw=always", show_error=True, target_func=log)
                if _cnt == None:
                    return None
                return bs4.BeautifulSoup(_cnt, "lxml")
            return soup

    def _download_image(self, url:str, filepath:str, log:callable) -> bool:
        '''下载图片'''

        content = self.spider.get_url(url, show_error=True, target_func=log)
        if content != None:
            _url = EHApi.get_image_src(content)
            if _url != None:
                return self.spider.download_file(_url, filepath, show_error=True, target_func=log)
            else:
                log("链接<{_url}>下载失败..")
        log("图片页面<{url}>下载失败..")
        return False

    def run(self, url:str) -> bool:
        '''启动下载任务'''

        # 检查URL格式是否正确
        if not EHApi.check_url_format(url):
            self.logsystem(f"链接URL<{url}>格式不正确")
            return (False, "链接URL格式不正确")

        # 下载主页面
        soup = self._download_main_page(url, self.logsystem)
        if soup == None:
            self.logsystem("主页面下载失败..")
            return (False, "主页面下载失败")
        
        # 解析所有基本信息
        title = EHApi.get_title(soup)
        title = clear_title(title)

        self.title = title

        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        else:
            self.say("警告:文件夹已经存在,可能存在覆盖下载")
            return (False, "文件夹已经存在,可能存在覆盖下载")

        images = EHApi.get_images(soup)
        urls = EHApi.get_extra_pages(url, soup)
        self.say(f"共找到{len(urls) + 1}个页面, 准备查询所有的图片")

        for page in urls:
            content = self.spider.get_url(page, show_error=True, target_func=self.logsystem)
            if content != None:
                _soup = bs4.BeautifulSoup(content, "lxml")
                if _images := EHApi.get_images(_soup):
                    images.extend(_images)

        self._total_count = len(images)
        self.say(f"成功找到{self._total_count}张图片,准备开始下载")

        for i, url in enumerate(images):
            filepath = f"{self.folder}/{i}.png"
            self.fetcher.insert((filepath, url))
        self.fetcher.press()
        return True, "启动成功"


class _ImageDownloader(AsyncReactor):
    '''图片下载器'''

    def __init__(self, spider: ConstantSpider, log, record):
        super().__init__("图片下载", log, coroutine_number=3)
        self.spider = spider
        self.error_recorder = Notes()
        self.errors = list()
        self.record = record

    async def handle(self, box: dict):
        filepath, url = box
        if self.spider.download_file(url, filepath, show_error=True, target_func=self.say):
            self.say(f"<{filepath}>下载成功!")
            self.record(True, os.path.basename(filepath))
        else:
            if self.error_recorder.point(filepath):
                self.insert(box)
            else:
                self.say(f"<{url}>超过重试次数,准备丢弃")
                self.errors.append(box)
                self.record(False, None)

class _ImageFetcher(AsyncReactor):
    '''图片链接获取'''

    def __init__(self, spider: ConstantSpider, downloader: _ImageDownloader, log, record):
        super().__init__("链接查询", log, coroutine_number=2)
        self.spider = spider
        self.downloader = downloader
        self.error_recorder = Notes()
        self.errors = list()
        self.record = record

    async def handle(self, box: dict):
        filepath, url = box
        if (cnt := self.spider.get_url(url, show_error=True, target_func=self.say)) != None:
            # 成功下载,解析重要链接并塞入ImageLoader

            _url = EHApi.get_image_src(cnt)
            if _url != None:
                self.say(f"成功获取链接<{filepath}>")
                self.downloader.insert((filepath, _url))
                if self.get_count() > 0:
                    if self.downloader.get_count() > 10:
                        self.downloader.press()
                else:
                    self.downloader.press()
            else:
                self.say(f"<{url}>无效")
                self.record(False, None)
        else:
            if self.error_recorder.point(filepath):
                self.insert(box)
            else:
                self.say(f"<{url}>超过重试次数,准备丢弃")
                self.errors.append(box)
                self.record(False, None)
