#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 09:33:42 2018

@author: derek
"""


class InterfaceMessage():
    imFirstIndex = 0
    imLastIndex = 1
    imAllIndex = 2

    # interface STATES
    imWaitingToConnect = 'WaitingToConnect'
    imConnected = 'Connected'
    imDisconnected = 'Disconnected'
    imStopped = 'Stopped'

    def __init__(self):
        self.input_ready = False
        self.input = []
        self.output_ready = False
        self.output = []

        self.connection_status = False
        self.state = self.imStopped

    def add_input(self, msg):
        self.input.append(msg)
        self.input_ready = True

    def has_input(self):
        if (len(self.input) > 0):
            return True
        return False

    def get_input(self, index=None, clear_buffer=False):

        msg = []

        if (index is None or index == InterfaceMessage.imFirstIndex):
            msg.append(self.input.pop(0))
        elif (index == InterfaceMessage.imLastIndex):
            msg.append(self.input.pop())
        elif (index == InterfaceMessage.imAllIndex):
            clear_buffer = True
            msg = self.input
        else:
            # throw exception?
            pass

        if (clear_buffer):
            self.input = []
        return msg

    def add_output(self, msg):
        self.output.append(msg)
        self.output_ready = True

    def has_output(self):
        if (len(self.output) > 0):
            return True
        return False

    def get_output(self, index=None, clear_buffer=True):

        msg = []

        if (index is None or index == InterfaceMessage.imFirstIndex):
            msg.append(self.output.pop(0))
        elif (index == InterfaceMessage.imLastIndex):
            msg.append(self.output.pop())
        elif (index == InterfaceMessage.imAllIndex):
            clear_buffer = True
            msg = self.output
        else:
            # throw exception?
            pass

        if (clear_buffer):
            self.output = []

        # print(self.output)
        return msg
