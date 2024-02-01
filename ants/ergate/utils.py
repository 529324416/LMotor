# -*- coding:utf-8 -*-
# /usr/bin/python3
# a simple script to provide some tools used in control spider

import threading
import calendar
import hashlib
import time
import json
import copy
import os
import re
# std supports

import configparser
from typing import Any
import requests
# third supports

zero_extend = lambda value:f"0{value}" if value < 10 else str(value)

def get_url(url, show_error=False, target_func=None, **kwargs):
    ''' post data to target url and get response data
    @url : the interface you want to post
    @show_error : output error information is show_error is True
    @target_func : the function to output error or save error to log file
    if target_func is None then post_url will use print instead
    @withstatus: if withstatus is true, then it will pack http status with return value
    @kwargs : the dict parameters of requests.post()'''

    try:
        res = requests.get(url, **kwargs)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        if show_error:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if target_func:
                target_func(error_info)
            else:
                print(error_info)
        return None
    
def download_url(url, filepath, show_error=False, target_func=None, **kwargs):

    try:
        res = requests.get(url, **kwargs)
        res.raise_for_status()
        with open(filepath,"wb") as f:
            f.write(res.content)
        return True
    except Exception as e:
        if show_error:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if target_func:
                target_func(error_info)
            else:
                print(error_info)
        return False

def post_url(url, data=None, show_error=False, target_func=None, **kwargs):
    ''' post data to target url and get response data
    @url : the interface you want to post
    @show_error : output error information is show_error is True
    @target_func : the function to output error or save error to log file
    if target_func is None then post_url will use print instead
    @withstatus: if withstatus is true, then it will pack http status with return value
    @kwargs : the dict parameters of requests.post()'''

    try:
        res = requests.post(url, data, **kwargs)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
        if show_error:
            if target_func:
                target_func(e,res)
            else:
                print(error_info)
        return None
    
async def async_get_url(url, show_error=False, target_func=None, **kwargs):
    ''' post data to target url and get response data
    @url : the interface you want to post
    @show_error : output error information is show_error is True
    @target_func : the function to output error or save error to log file
    if target_func is None then post_url will use print instead
    @withstatus: if withstatus is true, then it will pack http status with return value
    @kwargs : the dict parameters of requests.post()'''

    try:
        res = requests.get(url, **kwargs)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        if show_error:
            error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
            if target_func:
                target_func(error_info)
            else:
                print(error_info)
        return None

async def async_post_url(url, data=None, show_error=False, target_func=None, **kwargs):
    ''' post data to target url and get response data
    @url : the interface you want to post
    @show_error : output error information is show_error is True
    @target_func : the function to output error or save error to log file
    if target_func is None then post_url will use print instead
    @withstatus: if withstatus is true, then it will pack http status with return value
    @kwargs : the dict parameters of requests.post()'''

    try:
        res = requests.post(url, data, **kwargs)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        error_info = "error [ {} ] occurred when visit url:{}".format(str(e),url)
        if show_error:
            if target_func:
                target_func(e,res)
            else:
                print(error_info)
        return None


def save_json(obj,filepath,encoding='utf-8'):
    '''save txt information to local 
    @content: the content you want to save, it must be string type
    @filepath: the path you got to take content'''

    with open(filepath,"w",encoding=encoding) as f:
        f.write(json.dumps(obj,ensure_ascii=True))

def save_txt(text,filepath,encoding='utf-8'):
    '''save txt information to local 
    @content: the content you want to save, it must be string type
    @filepath: the path you got to take content'''

    with open(filepath,"w",encoding=encoding) as f:
        f.write(text)

def read_json(filepath,encoding='utf-8'):
    '''read json from local file to a dict
    @filepath: the json filepath, you must ensure that this function is existed'''

    with open(filepath,"r",encoding=encoding) as f:
        return json.load(f)

def read_txt(filepath,encoding='utf-8'):

    with open(filepath,'r',encoding=encoding) as f:
        return f.read()

def __rqheader2obj(headers,remove_first_line=True):
    ''' convert raw headers text to a python dict
    @headers : source headers '''

    index = 1 if remove_first_line else 0
    lines = headers.split("\n")[index:]
    _Ret = {}
    for _line in lines:
        if _line:
            index = _line.index(":")
            key,value = _line[:index],_line[index + 1:].strip()
            _Ret.setdefault(key,value)
    return _Ret

def headers_from_localfile(filepath,rmfirst_line=True,encoding='utf-8'):
    ''' read source headers from local txt file and 
    convert to a python dict
    @filepath: the file which saved the raw heades content'''

    with open(filepath,"r",encoding=encoding) as f:
        return __rqheader2obj(f.read(),remove_first_line=rmfirst_line)

def headers_from_raw(raw,rmfirst_line=True):
    ''' read source headers from local txt file and 
    convert to a python dict
    @filepath: the file which saved the raw heades content'''

    return __rqheader2obj(raw,remove_first_line=rmfirst_line)

def generate_md5(text:str) -> str:
    '''generate the md5 code of given text
    @text: the text you want to encode '''

    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()

class Date:
    ''' some functions about date'''

    def _date_infos():
        '''get year,month,day,hour,minutes and seconds'''

        _time = time.localtime()
        return _time[0],zero_extend(_time[1]),zero_extend(_time[2]),zero_extend(_time[3]),zero_extend(_time[4]),zero_extend(_time[5])

    def date_now():
        '''get time in format of yyyy-MM-dd (hh:mm:ss)'''

        return "{}-{}-{} ({}:{}:{})".format(*Date._date_infos())

    def get_today(connection="-"):
        '''get time in format of yyyy-MM-dd'''

        # print(Date._date_infos()[:3])
        return "{}&{}&{}".format(*Date._date_infos()[:3]).replace("&",connection)

    def format_yesterday_with_given_date(today,connection='-'):
        '''一个测试中的函数，求出today日期的前一天的日期
        @today: 当前的日期'''

        _year,_month,_day = tuple([int(_) for _ in today.split(connection)])
        _day -= 1
        if _day == 0:
            _month -= 1
            if _month == 0:
                _year -= 1
                _month,_day = 12,calendar.monthrange(_year,12)[1]
                return "{}{}{}{}{}".format(_year,connection,_month,connection,_day)
            _day = calendar.monthrange(_year,_month)[1]
            return "{}{}{}{}{}".format(_year,connection,zero_extend(_month),connection,_day)
        return "{}{}{}{}{}".format(_year,connection,zero_extend(_month),connection,zero_extend(_day))

class Counter:
    '''a count recorder, when the recorded count has touch a threshold
    then it will call a func you set for it'''

    def __init__(self,threshold:int,delegate:callable):
        '''set threshold and delegate'''

        assert isinstance(delegate,callable)
        self.delegate = delegate
        self.threshold = threshold
        self.count = 0

    def bind(self,delegate:callable)->None:
        '''set a new delegate for this'''

        assert isinstance(delegate,callable)
        self.delegate = delegate

    def increase(self,size=1):
        '''record for given count'''

        self.count += size
        if self.count >= self.threshold:
            self.delegate()

    def __call__(self,size=1):
        ''' call increase'''

        self.increase(size)
        
class Notes:
    '''_err_rcder would use dict to record a fail download record 
    or something other, if fail count has touch the threshold, then 
    this _err_rcder will thrown the recorder and tell the caller'''

    KEY = '_err_rcder_key'

    def __init__(self,threshold=5):
        '''initialize base attributes, note that, each record would saved in
        this note book must have the only id number to mark them, and this id number
        will be added automaticly'''

        self.threshold = threshold
        self._notes = dict()
    
    def point(self,workid:str) -> bool:
        ''' if this obj is first to record here, then it will be 
        add a new key call _err_rcder_key'''

        if self._notes.get(workid) is None:
            self._notes.setdefault(workid,1)
            return True
        if self._notes[workid] < self.threshold:
            self._notes[workid] += 1
            return True
        self._notes.pop(workid)
        return False

    def clear_all(self):

        self._notes.clear()

    def clear(self,workid:str) -> None:
        '''clear the _err_rcder_key in target obj
        @obj, the obj you saved in self._notes'''

        try:
            self._notes.pop(workid)
        except KeyError:
            pass

class Loog:
    '''a roll log implemention'''

    def __init__(self,logdir:str):
        ''' create base dir and initialize attributes
        @logdir: a folder to saved the log files
        @rollsize: this number determined that, how long a log file would be saved'''

        self._check_dir(logdir)
        self.lock = threading.Lock()
        self.date = Date.get_today(connection=".")
        self.append_new_file()

    def _check_dir(self,logdir:str) -> None:
        '''if target dir not existed, then it will be created
        @logdir: the target log folder path'''

        self.logdir = logdir
        if not os.path.exists(logdir):
            os.makedirs(logdir)

    def append_new_file(self):
        '''when a new file added, then the first file added to this list would be removed if 
        the length of first to last has exceeded self.rollsize
        @date: the name of target file'''

        filepath = "{}/{}.log".format(self.logdir,self.date)
        open(filepath,'w',encoding='utf-8').close()
        self.out = filepath

    def log(self,info):
        '''write a log to current log file
        @info: a string type value'''

        with self.lock:
            date = Date.get_today(connection='.')
            if date != self.date:
                self.date = date
                self.append_new_file()
            with open(self.out,"a",encoding='utf-8') as f:
                f.write("{}  {}\n".format(Date.date_now(),info))

    def __call__(self,info):
        self.log(info)

class Logger:
    '''save all information to single file'''

    def __init__(self,logpath:str):
        ''' create file'''

        self.logpath = logpath

    def log(self,info):
        '''log single information to target log file in json format
        info could be a string value or a dict value'''

        with open(self.logpath,"a",encoding='utf-8') as f:
            f.write(self.pack(info))
    
    def pack(self,info_group:dict):
        '''pack information into one dict
        @info_group:should be a dict'''

        return json.dumps({"time":Date.date_now(),"body":info_group},ensure_ascii=False) + "\n"
    
    def __call__(self, msg:str) -> Any:
        '''call log function'''

        self.log(msg)

class JsonDumper:
    '''load json file and set each key as python object's attributes
    deep type'''

    def __init__(self,obj):
        '''initialize base attributes
        @obj: the target object'''

        _obj = copy.deepcopy(obj)
        for k in _obj:
            if isinstance(_obj[k],dict):
                self.__setattr__(k,JsonDumper(_obj[k]))
            else:
                self.__setattr__(k,_obj[k])

class ConfigReader:
    '''read config file from config.ini and set them as 
    self's attributes '''

    def __init__(self,filepath):
        '''@filepath: point out filepath'''

        assert os.path.exists(filepath)
        self.source = configparser.ConfigParser()
        with open(filepath,"r",encoding='utf-8-sig') as f:
            self.source.readfp(f)
        self.__initialize_attributes()

    def __initialize_attributes(self):
        '''read all sections and options and set them 
        as attributes'''

        sections,tmp = self.source.sections(),dict()
        for _section in sections:
            options = self.source.options(_section)
            for _option in options:
                tmp.setdefault(_option,self.__handle_int_value(self.source.get(_section,_option)))
            self.__setattr__(_section,JsonDumper(tmp))
            tmp.clear()

    def __handle_int_value(self,text):
        '''convert string type of number value to int value'''

        result = re.search(r"int\(\d+\)",text)
        if result:
            return int(text.strip("int()"))
        return text