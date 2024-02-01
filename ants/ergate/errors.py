# -*- coding:utf-8 -*-
# /usr/bin/python3
# script provide different exception in building up driver chain

class __ergate_error(Exception):

    def __init__(self,message):
        super(__ergate_error,self).__init__()
        self.message = message
    
    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

class ErgateUnknownMinerType(__ergate_error):
    '''when you try to use an invalid miner type to create
    miner, then this error will be raised'''

    info = "Unknonw miner type, miner type has only 0 or 1 in this version"

    def __init__(self):
        super(ErgateUnknownMinerType,self).__init__(self.info)

class ErgateInvalidHandle(__ergate_error):
    '''if no handle function or callback function has been set
    and you try to create a handle function, then this error will be raised'''

    info = "No handle function has been set"

    def __init__(self):
        super(ErgateInvalidHandle,self).__init__(self.info)