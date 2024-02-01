# -*- coding:utf-8 -*-
# /usr/bin/python3
# try to use different async lib as the engine to run a miner
# whatever the lib is. the core mission of miner is to do all the
# jobs in given list

import threading
import asyncio
import queue

from ants.ergate.errors import *

class _miner(threading.Thread):
    ''' Miner would extended from _miner , _miner will has all features
    but it won't implement it'''

    def __init__(self,handle,cb,workercb):
        '''receive basic components
        @handle: a function to solve missions
        @cb: a function to send the result of handle to other ergate node
        @workercb: when all missions has done, then restart the ergate_node'''

        super(_miner,self).__init__()
        self.handle = handle
        self.cb = cb
        self.workercb = workercb

    def dump_missions(self,works):
        ''' this function would recv a batch of works
        and put them into self's work queue'''

        raise NotImplementedError()

    def solve_missions(self):
        '''in this version of ergate, solve missions should be the function
        which start to handle all works'''

        raise NotImplementedError()

    def is_worker_free(self):
        '''check if worker is not working now'''

        return not self.is_alive()

    def get_count(self):
        '''record how many work left in current mission queue'''

        raise NotImplementedError()

class _sync_miner(_miner):
    '''_sync_miner is a batch worker which run in 
    synchronous mode'''

    def __init__(self,handle,cb,threadcb):
        super(_sync_miner,self).__init__(handle,cb,threadcb)
        self.missions = queue.Queue()

    def dump_missions(self,works:queue.Queue):
        '''dump all missions to self.__missions
        @works: this must be a queue.Queue'''

        while not works.empty():self.missions.put(works.get())
        
    def solve_missions(self):
        '''iterate self.__missions and handle all works in sychronous mode'''

        while not self.missions.empty():
            self.cb(self.handle(self.missions.get()))

    def run(self):
        '''start to run sync miner'''

        self.solve_missions()
        self.workercb()                
        # * restart the remain works

    def get_count(self):
        '''get how many works left in current queue'''

        return self.missions.qsize()

class _async_miner(_miner):
    '''async miner require anything controlled by this object to be a 
    coroutine, async miner will split the works into serval parts, the number of 
    parts will defined by user'''

    def __init__(self,handle,cb,threadcb,split=2):
        '''receive all informations'''

        super(_async_miner,self).__init__(handle,cb,threadcb)
        self.coroutine_number = split
        self.coroutines = list()
        self.__counters = list()
    
    def dump_missions(self,works:queue.Queue):
        '''dump all missions into two coroutine'''

        coroutine_size = int(works.qsize() / self.coroutine_number)
        for idx in range(self.coroutine_number - 1):
            self.coroutines.append(self.make_coroutine(works,coroutine_size))
        self.coroutines.append(self.make_coroutine(works,works.qsize()))

    def make_coroutine(self,missions,size):
        '''create a coroutine according to size
        @missions: the total works
        @size: how many works would this coroutine take'''

        tmp = queue.Queue()
        for idx in range(size):
            tmp.put(missions.get())
        self.__counters.append(tmp)
        return self.solve_missions(tmp)

    async def solve_missions(self,missions):
        '''this function will return a coroutine contained a group of 
        missions, and it need to be run with a new loop'''

        while not missions.empty():
            result = await self.handle(missions.get())
            await self.cb(result)

    async def solve(self):
        ''' the top of coroutine'''

        await asyncio.gather(*tuple(self.coroutines))

    def run(self):
        '''thread start'''

        asyncio.run(self.solve())
        self.workercb()

    def get_count(self):
        '''get how many works left in current mission queues'''

        _s = 0
        for q in self.__counters:_s += q.qsize()
        return _s

class _sync_miner_context(_sync_miner):
    '''add config function and ending callback in sync miner'''

    def __init__(self,handle,cb,threadcb,cfg_func,cfg_func_ending):
        ''' in this object, cfg_func and cfg_func_ending should be a common function'''

        super(_sync_miner_context,self).__init__(handle,cb,threadcb)
        self.cfg_func = cfg_func
        self.cfg_func_ending = cfg_func_ending

    def solve_missions(self):
        '''run config function and ending function'''

        self.cfg_func()
        super().solve_missions()
        self.cfg_func_ending()

class _async_miner_context(_async_miner):
    ''' add config function and ending callback in async miner'''

    def __init__(self,handle,cb,threadcb,cfg_func,cfg_func_ending,split=2):
        ''' in this object, cfg_func, and cfg_func_ending should be a async function'''

        super(_async_miner_context,self).__init__(handle,cb,threadcb,split=split)
        self.cfg_func = cfg_func
        self.cfg_func_ending = cfg_func_ending

    async def solve(self):
        '''rewrite solve function for we can add some prefixed configs'''

        await self.cfg_func()
        await asyncio.gather(*tuple(self.coroutines))
        await self.cfg_func_ending()

class MinerType:
    '''Miner has two type in different running mode but has same interface
    this class will record two type and use them to mark the miner'''

    SYNC_MINER = 0
    ASYNC_MINER = 1
    SYNC_MINER_CONTEXT = 2
    ASYNC_MINER_CONTEXT = 3

class MinerCreater:
    ''' a simple object help to generate miner, and split the miner create process 
    from marionette'''

    def __init__(self,handle,cb,miner_type=MinerType.SYNC_MINER,coroutine_number=2,cfg_func=None,cfg_func_ending=None):
        '''set options at this place'''

        self.miner_type = miner_type
        self.coroutine_number = coroutine_number
        self.handle = handle
        self.cb = cb
        self.cfg_func = cfg_func
        self.cfg_func_ending = cfg_func_ending

    def set_handle(self,handle):
        '''reset handle function for creater, this function will
        be useful if you try to change the miner dynamicly'''

        self.handle = handle

    def set_cb(self,cb):
        '''reset callback function for creater
        @cb: the callback function'''

        self.cb = cb

    def __call__(self,threadcb):
        ''' when you call this object, it will return a new miner'''

        if self.miner_type == MinerType.SYNC_MINER:
            return _sync_miner(self.handle,self.cb,threadcb)
        elif self.miner_type == MinerType.ASYNC_MINER:
            return _async_miner(self.handle,self.cb,threadcb,split=self.coroutine_number)
        elif self.miner_type == MinerType.SYNC_MINER_CONTEXT:
            return _sync_miner_context(self.handle,self.cb,threadcb,self.cfg_func,self.cfg_func_ending)
        elif self.miner_type == MinerType.ASYNC_MINER_CONTEXT:
            return _async_miner_context(self.handle,self.cb,threadcb,self.cfg_func,self.cfg_func_ending,split=self.coroutine_number)
        else:
            raise ErgateUnknownMinerType()

class Marionette:
    ''' the base class of marionette, and this object will controll a 
    miner to run all missions'''

    def __init__(self,miner_generator):
        '''initiailze base attributes
        @handle: the handle function to run all parameters
        @cb: the callback function to determine the how to handle the result of handle function'''

        self._missions = queue.Queue()
        self._lock = threading.Lock()
        self._current_worker = None
        self.miner_generator = miner_generator
        #* Marionette doesn't known how to create a miner but 
        #* just call it to get a miner

    def get_count(self):
        '''compue how many datas has not been handled'''

        if self._current_worker is None:
            return self._missions.qsize()
        return self._missions.qsize() + self._current_worker.get_count()

    def get_local_count(self):
        '''how many works left in current marionette'''

        return self._missions.qsize()

    def rest_time(self,interval=1):
        '''compute how much time would left times take'''

        return self.get_count() * interval

    def insert(self,item):
        '''insert a new work to this marionette
        @item: an item that would be handled by handle function'''

        with self._lock:
            self._missions.put(item)

    def insert_many(self,items):
        '''insert a group of items to this marionette
        @items: should be a list and each element is an item would be handled 
        by handle function'''

        with self._lock:
            for item in items:self._missions.put(item)

    def press(self):
        '''if current worker is not working now, if not working then we check 
        if has work needed to to, if true then we start it
        otherwise we save the requests into a counter
        '''

        if self._missions.qsize() > 0:
            if self._current_worker is None or self._current_worker.is_worker_free():
                self.__operate()

    def __operate(self):
        '''start to run miner, this function
        would dump all missions in self._missions and start to run it'''

        self._current_worker = self.miner_generator(self.callback)
        self._current_worker.dump_missions(self._missions)
        self._current_worker.start()

    def callback(self):
        '''when a miner has work done, then it should ask marionette 
        to handle left works'''

        if self._missions.qsize() > 0:
            if self._current_worker.get_count() == 0:
                self.__operate()

    def anything_done(self):
        '''if there is no work in current work and no work in marionette
        then this func will return true'''

        if self._current_worker is None:
            return self._missions.qsize() == 0
        return self._current_worker.is_worker_free() and self._missions.qsize() == 0

class __reactor:
    '''Reactor is a base unit you need to extend, rewrite two function 
    handle and callback, it will initialize miner_creater and marionette to control them'''

    def __init__(self,name,log=print):
        '''initialize base attributes'''

        self.name = name
        self.log = log

    def create_miner_generator(self,**kwargs):
        ''' initialize a miner_creater according to miner_type'''

        self._miner_creater = MinerCreater(self.handle,self.callback,**kwargs)

    def insert(self,box):
        '''insert box into marionette
        @box: the data you want to handle'''

        self.marionette.insert(box)

    def insert_many(self,boxes):
        '''insert a list of boxes into marionette
        @boxes: a list contained many box'''

        self.marionette.insert_many(boxes)

    def rest_time(self,interval=1):
        '''compute how much time would cost to handle all boxes
        @interval: the time length of each box would cost,default is 1 second'''

        return self.marionette.rest_time(interval=interval)

    def anything_done(self):
        '''check if all works has done'''

        return self.marionette.anything_done()

    def get_count(self):
        '''get how many works left in current reactor'''

        return self.marionette.get_count()

    def handle(self,box:dict):
        '''this function need to be rewrite, this function's return value
        must be in the structure of (id,data), id is the next reactor the data would go
        data is the value would be sent, data could be the value in any type 
        @box: data type handled by this function'''

        raise NotImplementedError()
        # func must be rewrite or this Reactor wont't do anything.

    def callback(self,box:tuple):
        '''callback will determine where would the result of handle function go
        box must be in the format of (id,box), id represent another Reactor(maybe self)'''

        raise NotImplementedError()
        # function should be rewrite for async or sync

    def marionette_configs(self):
        '''function would call when marionette ready to run
        this must be a function without any parameters'''

        raise NotImplementedError()

    def marionette_callback(self):
        '''function would call when marionette has workdone
        this must be a function without any parameters'''

        raise NotImplementedError()

    def say(self,info):
        '''output a info with '''

        if self.log is None : return
        self.log(f"[-{self.name}-] {info}")

class SyncReactor(__reactor):
    '''Reactor is synchronous, this Class would only help you to create base function and 
    set a miner_type'''

    def __init__(self,name,log):
        ''' initialize reactor_base'''

        super(SyncReactor,self).__init__(name,log=log)
        self.create_miner_generator(miner_type=MinerType.SYNC_MINER)
        self.marionette = Marionette(self._miner_creater)

    def callback(self,box):
        ''' base function would do nothing here'''
        pass

    def press(self):
        self.marionette.press()

class CtxSyncReactor(__reactor):
    '''reactor would add config function before run marionette's play function'''

    def __init__(self,name,log):
        ''' initialize reactor_base'''

        super(CtxSyncReactor,self).__init__(name,log=log)
        self.create_miner_generator(miner_type=MinerType.SYNC_MINER_CONTEXT,cfg_func=self.marionette_configs,cfg_func_ending=self.marionette_callback)
        self.marionette = Marionette(self._miner_creater)

    def callback(self,box):
        '''base function would do nothing here'''
        pass

    def marionette_callback(self):
        ''' call after miner has run'''
        pass

    def marionette_configs(self):
        '''call before miner would run'''
        pass

    def press(self):
        self.marionette.press()

class AsyncReactor(__reactor):
    '''the async version of sync miner'''

    def __init__(self,name,log,coroutine_number=2):
        ''' initialize __reator'''

        super(AsyncReactor,self).__init__(name,log=log)
        self.create_miner_generator(miner_type=MinerType.ASYNC_MINER,coroutine_number=coroutine_number)
        self.marionette = Marionette(self._miner_creater)

    async def callback(self,box):
        ''' a asynchronous callback function'''
        pass

    def press(self):
        self.marionette.press()

class CtxAsyncReactor(__reactor):
    '''reactor would add config function before run marionette's play function'''

    def __init__(self,name,log,coroutine_number=2):
        ''' initialize reactor_base'''

        super(CtxAsyncReactor,self).__init__(name,log=log)
        self.create_miner_generator(miner_type=MinerType.ASYNC_MINER_CONTEXT,coroutine_number=coroutine_number,cfg_func=self.marionette_configs,cfg_func_ending=self.marionette_callback)
        self.marionette = Marionette(self._miner_creater)

    async def callback(self,box):
        '''base function would do nothing here'''
        pass

    async def marionette_callback(self):
        ''' call after miner has run'''
        pass

    async def marionette_configs(self):
        '''call before miner would run'''
        pass

    def press(self):
        self.marionette.press()