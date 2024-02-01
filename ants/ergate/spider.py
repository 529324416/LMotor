# -*- coding:utf-8 -*-
# /usr/bin/python3
# this script will used the code in other partial to build up the spider
# components here

from os import error
from ants.ergate.utils import *

class ConstantSpider:
    ''' login to target website and keep connection status
    for some sites which need login to get some information ...'''

    def __init__(self,headers=None,**kwargs):
        ''' initialize login module with a session
        and any other action about visiting Internet will based on
        this session 
        @headers:if headers is not None, then spider will use given
        headers as request header'''

        self.sess = requests.session(**kwargs)
        if headers:self.install_headers(headers)
        self.pack = None

    def get_url(self, url, show_error=False, target_func=None, **kwargs):
        ''' download html source code from given url
        @url : the target url you want to get
        @show_error : this function will output error information
        if show_error is True
        @target_func : the function to output error or save error to log file
        if target_func is None then , this function will use print instead
        @kwargs : the dict parameters of requets.get()'''

        try:
            res = self.sess.get(url, **kwargs)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            return res.text
        except Exception as e:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if show_error:
                if target_func:
                    target_func(error_info)
                else:
                    print(error_info)
            return None

    def download_file(self, url, filepath, show_error=False, target_func=None, **kwargs):

        try:
            res = self.sess.get(url, **kwargs)
            res.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if show_error:
                if target_func:
                    target_func(error_info)
                else:
                    print(error_info)
            return False
        
    def download_content(self, url, show_error=False, target_func=None, **kwargs):

        try:
            res = self.sess.get(url, **kwargs)
            res.raise_for_status()
            return res.content
        except Exception as e:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if show_error:
                if target_func:
                    target_func(error_info)
                else:
                    print(error_info)
            return None


    def post_url(self, url, data=None, show_error=False, target_func=None, **kwargs):
        ''' post data to target url and get response data
        @url : the interface you want to post
        @show_error : output error information is show_error is True
        @target_func : the function to output error or save error to log file
        if target_func is None then post_url will use print insted
        @kwargs : the dict parameters of requests.post()'''

        try:
            res = self.sess.post(url, data, **kwargs)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            return res.text
        except Exception as e:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if show_error:
                if target_func:
                    target_func(error_info)
                else:
                    print(error_info)
            return None

    def install_headers(self,headers):
        '''use given headers as request header for target 
        website, and this action will rewrite old headers 
        @headers: the headers you want to set '''

        self.sess.headers = headers

    def set_proxies(self,proxies):
        '''set proxies for current session'''

        self.sess.proxies = proxies

    def get_cookies(self):
        ''' get cookies in string type '''

        return requests.utils.dict_from_cookiejar(self.sess.cookies)

    def set_cookies(self,cookies):

        self.sess.cookies = requests.utils.cookiejar_from_dict(cookies)