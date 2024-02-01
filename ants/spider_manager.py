import hashlib
import ants.ehspider as ehspider


default_proxies = {"https":"socks5://127.0.0.1:10808"}


__running_spider = { }
def run_ehspider(url:str, spider_id:str, gallery_folder:str, callback:callable=None):
    '''start to run ehspider and return if success'''

    if url is None or len(url) == 0:
        return False, "invalid url"
    
    if gallery_folder is None or len(gallery_folder) == 0:
        return False, "invalid gallery folder"

    if spider_id in __running_spider:
        return False, "spider is already started"
    spider = ehspider.EhSpider(f"{gallery_folder}/{spider_id}", default_proxies, callback)
    __running_spider.setdefault(spider_id, spider)
    success, msg = spider.run(url)
    if not success:
        __running_spider.pop(spider_id)
        return False, msg
    return True, spider_id