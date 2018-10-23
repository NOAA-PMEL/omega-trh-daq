#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:35:11 2018

@author: derek
"""
import asyncio
import functools
import logging
import sys
import time
from ifmessage import InterfaceMessage

SERVER_ADDRESS = ('localhost', 8199)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('main')


class TCPClient(asyncio.Protocol):

    #connections = {}

    # def __init__(self, messages, future):
    def __init__(self, im_message):
        super().__init__()
        #self.messages = messages
        self.log = logging.getLogger('TCPClient')
        self.data_ready = False
        self.buffer = ''
 #       self.signature = signature
        self.im_message = im_message
        self.im_message.state = InterfaceMessage.imStopped
        # print(self)
        #self.f = future

    def connection_made(self, transport):
        print('connection made')
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.log = logging.getLogger(
            'TCPClient_{}_{}'.format(*self.address)
        )
        self.im_message.connection_status = True
        self.im_message.state = InterfaceMessage.imConnected

        # print(self.transport)
        #TCPClient.connections[self.signature] = {'data_ready':False, 'buffer':''}
        #self.log.debug('connection accepted')
        #SensorServer.clients[self.address] = self.transport
        # print(SensorServer.clients)

    def data_received(self, data):
        # print(data)
        #self.log.debug('received {!r}'.format(data))
        self.buffer = data
        # print(self.buffer.decode('utf-8'))
        # print(self.buffer)
        self.data_ready = True
        #TCPClient.connections[self.signature] = {'data_ready':True, 'buffer':data}
        self.im_message.add_output(data)
        # dprint(data)
        # print(self.im_message)
        # print(TCPClient.connections)
        # self.transport.write(data)
        #self.log.debug('sent {!r}'.format(data))
        # self.broadcast(data)

    def eof_received(self):
        self.log.debug('received EOF')
        self.transport.close()
        self.im_message.connection_status = False
        self.im_message.state = InterfaceMessage.imDisconnected
        #del TCPClient.connections[self.signature]
        # if self.transport.can_write_eof():
        #    self.transport.write_eof()

    def connection_lost(self, error):
        self.log.debug('server closed connection')
        self.transport.close()
        self.im_message.connection_status = False
        self.im_message.state = InterfaceMessage.imDisconnected
        #del TCPClient.connections[self.signature]
#        if error:
#            self.log.error('ERROR: {}'.format(error))
#        else:
#            self.log.debug('closing')
#
#        del SensorServer.clients[self.address]
#        print(SensorServer.clients)
        super().connection_lost(error)

#    def has_data(self,signature):
#        #return TCPClient.connections[signature]['data_ready']
#        return self.im_message.has_message()
#
#
#    def get_buffer(self,signature):
#        #print('buffer')
#        result = TCPClient.connections[signature]['buffer']
#        TCPClient.connections[signature] = {'data_ready':False, 'buffer':''}
#        #print(result)
#        return result


async def read_buffer(im_message):
    while True:
        # write to clients
        # print("T=25.0,RH=34.5")
        # srv.send_to_clients("T=25.0,RH=34.5")
        start = time.time()
        # srv.send_to_clients(sensor.read())
        # if (False):
        if (im_message.has_output()):
            buffer = im_message.get_output(clear_buffer=False)[0].decode('utf-8')
            print('buffer : ' + buffer)

        end = time.time()
        delta = end-start
        while (delta > 1):
            delta -= 1.0
        #print('delta = %3.2f, sleep = %3.2f' % (delta, (1-delta)))
        # print("read_sensor")
        # await asyncio.sleep(1.0-delta)
        await asyncio.sleep(0.1)
        # await asyncio.sleep(.5)
        # yield from asyncio.sleep(1)


def shutdown():
    tasks = asyncio.Task.all_tasks()
    for t in tasks:
        # print(t)
        t.cancel()
    #print("Tasks canceled")
    asyncio.get_event_loop().stop()
    # await asyncio.sleep(1)


if __name__ == "__main__":

    signature = "abcdef"

    #sensor = SHT31()
    #sensor = HumiChip()
    #sensor = DummyTRHP()
    #tcp = TCPClient()

    im_message = InterfaceMessage()
    client_factory = functools.partial(
        TCPClient,
        im_message=im_message,
    )

    event_loop = asyncio.get_event_loop()
    factory = event_loop.create_connection(client_factory, *SERVER_ADDRESS)
    #factory = event_loop.create_connection(tcp, *SERVER_ADDRESS)
    #server = asyncio.ensure_future(factory)
    client = event_loop.run_until_complete(factory)

    task = asyncio.ensure_future(read_buffer(im_message))
    task_list = asyncio.Task.all_tasks()

    try:
        event_loop.run_until_complete(asyncio.wait(task_list))
        # event_loop.run_forever()
    except KeyboardInterrupt:
        print('closing client')
        # client.close()
        # event_loop.run_until_complete(client.wait_closed())

        shutdown()
#        for task in task_list:
#            print("cancel task")
#            task.cancel()
        # server.close()
        event_loop.run_forever()
        # event_loop.run_until_complete(asyncio.wait(asyncio.ensure_future(shutdown)))

    finally:

        print('closing event loop')
        event_loop.close()
