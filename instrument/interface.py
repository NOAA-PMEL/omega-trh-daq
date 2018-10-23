#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:20:13 2018

@author: derek
"""

from abc import ABCMeta, abstractmethod
import asyncio
#from erd.daq.daq import DAQ
from datetime import datetime

import random

"""
Interface
Abstract base class for HW Interface between Instrument class and "hardware". 
Interface requires:
   - event loop (asyncio) 
   - configuration (dictionary with hw specific values)
"""


class Interface(ABCMeta):

    def __init__(self):
        super().__init__()
        self.name = None
        self.type = None
        self.loop = None

        #self.info = InterfaceInfo
        #self.config = InterfaceConfig
        self.inputs = []
        self.outputs = []
        self.is_running = False

        self.read_buffer = {}
        # write_buffer?

    @abstractmethod
    def open(self):
        pass

    def start(self):
        print("Starting "+self.name)
        task = asyncio.ensure_future(self.read_loop())
        self.task_list.append(task)
        self.is_running = True
        self.read_buffer['default'] = ''

    def stop(self):
        print("stopping "+self.name)
        tasks = asyncio.Task.all_tasks()
        for t in self.task_list:
            t.cancel()
            tasks.remove(t)
        self.is_running = False

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def configure(self):  # second arg will be config info
        pass

    def read(self, buffer='default'):
        return self.read_buffer[buffer]

    @abstractmethod
    def get(buf):
        pass

    async def read_loop(self):
        while self.is_running:
            #print('in iface:read_loop')
            # print(self.read_buffer)
            for key in self.read_buffer.keys():
                # print("read_loop["+key+"]")
                self.get(key)

            await asyncio.sleep(.25)

    def get_timestamp(self):
        return datetime.utcnow()
    # @property
    # def inputs(self):
    #     return self.input_list

    # @inputs.setter
    # def inputs(self,input_list):
    #     self.input_list = input_list

    # def add_input(iface_input):
    #     self.input_list.append(iface_input)

    # def output_list():
    #     return self.output_list

    # def output_list(output_list):
    #     self.output_list = output_list

    # def add_output(iface_output):
    #     self.output_list.append(iface_output)


class SerialPort(Interface):

    def __init__(self):
        super().__init__(self)

    def open(self):
        pass

    def close(self):
        pass

    def configure(self):
        pass

    def get(buf):
        pass


class TCPPort(Interface):

    def __init__(self):
        super().__init__()
        self.name = 'TCPPort'

    def open(self):
        pass

    def close(self):
        pass

    def configure(self):
        pass

    def get(buf):
        pass


class DummyPort(Interface):

    def __init__(self):
        super().__init__()
        self.name = "DummyPort"

    def open(self):
        pass

    def close(self):
        pass

    def configure(self):
        pass

    def get(self, buf):
        # print("DummyPort:get("+buf+")")

        # dummy data
        #        dat = '16.4,18.2,1000.4,12,status=OK\n'

        dat = str(random.uniform(13, 15))+','+str(random.uniform(16, 19))+',' + \
            str(random.uniform(990, 1020))+','+str(random.uniform(11, 13))+',status=OK\n'
        self.read_buffer[buf] = (self.get_timestamp(), dat)
        # print('Interface.get:')
        # print(self.read_buffer[buf])
        # print(self.read_buffer)
        # print(dat)
