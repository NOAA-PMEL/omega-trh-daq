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
from tcpclient import TCPClient
from ifmessage import InterfaceMessage
from data import Data
from datetime import datetime
import json

SERVER_ADDRESS = ('localhost', 8199)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('main')


class InterfaceManager():

    def __init__(self):
        self.interface_list = {}
        self.task_list = []


#    config = {'client_sig': client_sig,
#              'server_address': server_address,
#              'data': data,
#              }

#    def createTCPInterface(self,client_sig,server_address,data):
    def createTCPInterface(self, client_sig, server_address, data):
        iface_name = '{}_{}_{}'.format(client_sig, server_address[0],
                                       server_address[1])

        try:
            print('createTCPInterface')
            self.interface_list[iface_name] = {
                'name': iface_name,
                'auto_connect': True,
                'connected': True,
                'server_address': server_address,
                'data': data,
                'iface': TCPInterface(server_address, data),
            }

            #iface.do_reconnect = False
            #print('starting interface')
            # self.interface_list[iface_name]['iface'].start()
            # self.interface_list[iface_name]['iface'].connect()

        except Exception as e:
            print('create: exception: {}'.format(e))
            self.interface_list[iface_name]['connected'] = False
            self.interface_list[iface_name]['iface'] = None

        # self.task_list.append(asyncio.ensure_future(self.check_connection()))
        # return self.interface_list[iface_name]['iface']
        # print(self.interface_list[iface_name])
        return self.interface_list[iface_name]

    async def check_connection(self):

        while True:
            for key in self.interface_list:

                print('check_connection: {}'.format(key))
                # print(self.interface_list[key]['iface'].im_message.state)

                if self.interface_list[key]['auto_connect']:
                    print('here:1')
#
                    print(self.interface_list[key]['iface'] is not None)
#                    if (self.interface_list[key]['iface'] is not None and
#                        self.interface_list[key]['ifacd'].im_message.state ==
                    if (self.interface_list[key]['iface'] is not None and
                        (self.interface_list[key]['iface'].im_message.state == InterfaceMessage.imWaitingToConnect or
                         self.interface_list[key]['iface'].im_message.state == InterfaceMessage.imDisconnected)):
                        print('here:2')
                        del self.interface_list[key]['iface']
                        self.interface_list[key]['iface'] = None
                        print('here:3')
#
#
                        try:
                            print('here:4')
                            self.interface_list[key]['iface'] = TCPInterface(self.interface_list[key]['server_address'],
                                                                             self.interface_list[key]['data'])
                            print('here:5')
                            self.interface_list[key]['connection'] = True
                            self.interface_list[key]['iface'].connect()
                            print('here:6')
                            # self.interface_list[key]['iface'].start()
                            print('here:7')
                        except:
                            print('here:8')
                            self.interface_list[key]['iface'] = None
                            self.interface_list[key]['connected'] = False

                    #print('check_connection status: {}'.format(self.interface_list[key]['iface'].im_message.status))

#                    print('a')
#                    print(self.interface_list[key]['connected'])
#                    #if self.interface_list[key]['iface'] is None:
#                    #    print('is none')
#                    #print('connection_status: {}'.format(self.interface_list[key]['iface'].im_message.conenection_status))
# if (
# self.interface_list[key]['iface'] is None or
# (self.interface_list[key]['iface'].is_running and
# not self.interface_list[key]['iface'].is_connected)
# ):
#                    #if not self.interface_list[key]['connected']:
#                    if not self.interface_list[key]['iface'].im_message.connection_status:
#                        print('b')
# if (self.interface_list[key]['iface'] is not None):
##                            del self.interface_list[key]['iface']
# print('c')
#                            #print(self.interface_list['key']['iface'])
#                        del self.interface_list[key]['iface']
#
#                        try:
#                            print('d')
#                            self.interface_list[key]['iface'] = TCPInterface(self.interface_list[key]['server_address'],
#                                               self.interface_list[key]['data'])
#                            self.interface_list[key]['connection'] = True
#                            self.interface_list[key]['iface'].open()
#                            self.interface_list[key]['iface'].start()
#                            print('e')
#                        except:
#                            print('f')
#                            self.interface_list[key]['iface'] = None
#                            self.interface_list[key]['connected'] = False
#
#                    print('end of if 1')
#                print('end of if 2')
            print('sleep:5')
            await asyncio.sleep(5.0)


class TCPInterface():
    ifStopped = 'Stopped'
    ifStarting = 'Starting'
    ifDoConnect = 'DoConnect'
    ifWaitingToConnect = 'WaitingToConnect'
    ifConnected = 'Connected'
    ifDisconnected = 'Disconnected'
    ifStopping = 'Stopping'

    def __init__(self, server_address, data):

        self.client = None
        self.im_message = InterfaceMessage()
        self.server_address = server_address
        self.loop = asyncio.get_event_loop()

        self.task_list = []
        #self.task_list['client'] = None
        self.state = self.ifStopped
        self.connection_timeout = 0

        self.is_running = False
        self.attempt_connect = False
        self.is_connected = False
        self.auto_reconnect = False
        self.do_reconnect = False
        self.connection = None

        self.read_buffer = []
        self.data = data

        self.timeid = datetime.utcnow()

        self.open()

    async def do_connect3(self):

        while True:
            if self.state == self.ifDoConnect or self.state == self.ifDisconnected:
                print('STATE: {}'.format(self.state))

                if self.client is not None:
                    self.client.cancel()

                client_factory = functools.partial(
                    TCPClient,
                    im_message=self.im_message,
                )

                try:
                    print('attempting to connect')
                    con = self.loop.create_connection(client_factory, *self.server_address)
                    # print(con)
                    self.client = asyncio.Task(con)
                    # print(self.client)
                    asyncio.ensure_future(self.client)
                    self.state = self.ifWaitingToConnect
                except Exception as e:
                    print('TCPInterface.connect Exception: {}'.format(e))
                    self.state = self.ifDoConnect

            await asyncio.sleep(1)


#        client_factory = functools.partial(
#                TCPClient,
#                im_message=self.im_message,
#                )
#
#        try:
#            print('a')
#            con = self.loop.create_connection(client_factory, *self.server_address)
#            self.connection = con
#            print('b')
#
##        self.auto_reconnect = True
##        self.im_message.connection_status = True
##        self.is_connected = True
##        self.do_reconnect = True
##        self.attempt_connect = False
#            print('c')
#            asyncio.ensure_future(con)
#            print('d')
#        except Exception as e:
#            print('TCPInterface.connect exception: {}'.format(e))

    def open(self):
        print('iface: open')
#        client_factory = functools.partial(
#                TCPClient,
#                im_message=self.im_message,
#                )
#
#        factory = self.loop.create_connection(client_factory, *self.server_address)
#        #factory = event_loop.create_connection(tcp, *SERVER_ADDRESS)
#        #server = asyncio.ensure_future(factory)
#        self.loop.run_until_complete(factory)
        self.attempt_connect = False
        #task = asyncio.ensure_future(self.do_connect())
        #task = self.loop.run_until_complete(self.do_connect())
        # self.task_list.append(task)

        try:
            task = asyncio.ensure_future(self.do_connect3())
            self.task_list.append(task)
        except Exception as e:
            print('open exception: {}'.format(e))

#        client_factory = functools.partial(
#                TCPClient,
#                im_message=self.im_message,
#                )
        # print(self.loop)
        # print(self.im_message)
        # print(self.server_address)
        #factory = self.loop.create_connection(client_factory, *self.server_address)
        # print(factory)
        #client = self.loop.run_until_complete(factory)
        # print(client)
        #self.is_connected = True
        # print(self.loop)

    def start(self):
        print("Starting ")

        self.state = self.ifStarting

        self.attempt_connect = True
        task = asyncio.ensure_future(self.read_loop())
        self.task_list.append(task)
        task2 = asyncio.ensure_future(self.check_connection())
        self.task_list.append(task2)
        self.state = self.ifDoConnect

        self.is_running = True
        #self.read_buffer['default'] = ''

    def stop(self):
        #print("stopping "+self.name)
        self.auto_reconnect = False
        self.attempt_connect = False
        self.is_running = False

        self.state = self.ifStopping

        self.client.cancel()

        #tasks = asyncio.Task.all_tasks()
        for t in self.task_list:
            # print('tcpinterface.stop():')
            # print(t)
            t.cancel()
            self.task_list.remove(t)
            # tasks.remove(t)
        #self.attempt_connect = False
        self.state = self.ifStopped

    def has_data(self):
        # print(len(self.read_buffer))
        # f (len(self.read_buffer)>0):
        if (self.data.size() > 0):
            return True
        return False

    def read(self):
        # print('read_data')
        # print(self.read_buffer)
        return self.data.get()
        #buffer = self.read_buffer.pop(0)
        #buffer = [1]
        #print('\n\n' + buffer + '\n\n')
        #del self.read_buffer[:]
        # print(buffer)
#        return [1]

    def write(self, msg):

        self.im_message.add_input(msg)

#    @abstractmethod
#    def close(self):
#        pass
#
#    @abstractmethod
#    def configure(self): #second arg will be config info
#        pass
#
#    def read(self,buffer='default'):
#        return self.read_buffer[buffer]
#
#    @abstractmethod
#    def get(buf):
#        pass

    async def do_connect2(self):

        if self.im_message.state == InterfaceMessage.imWaitingToConnect:
            try:
                print('here:1')
                # tcp_server = yield from loop.create_connection(TcpClient,
                print('attempting connect')
                client_factory = functools.partial(
                    TCPClient,
                    im_message=self.im_message,
                )
                print('here:2')
                # print(self.loop)
                # print(self.im_message)
                # print(self.server_address)
                factory = self.loop.create_connection(client_factory, *self.server_address)
                self.connection = factory

                self.auto_reconnect = True
                self.im_message.connection_status = True
                self.is_connected = True
                self.do_reconnect = True
                self.attempt_connect = False
                print('here:3')
                # print(factory)
                print('here:4')
                asyncio.ensure_future(factory)
                # asyncio.ensure_future(asyncio.Task(factory))
                #self.connection = asyncio.Task(factory)
                print(self.connection)
                print(self.timeid)
                #client = self.loop.run_until_complete(factory)
                print("client complete")
            except Exception as e:
                self.im_message.connection_status = False
                self.is_connected = False
                print("client exception occurred: {}".format(e))

        print('do_connect2: done')
        await asyncio.sleep(0)

    async def do_connect(self):
        print('do_connect')
        print(self.attempt_connect)
        print(self.is_connected)
        while True:
            print(self.attempt_connect)
            print(self.im_message.connection_status)
            if self.attempt_connect and not self.im_message.connection_status:
                try:
                    print('here:1')
                    # tcp_server = yield from loop.create_connection(TcpClient,
                    print('attempting connect')
                    client_factory = functools.partial(
                        TCPClient,
                        im_message=self.im_message,
                    )
                    print('here:2')
                    # print(self.loop)
                    # print(self.im_message)
                    # print(self.server_address)
                    factory = self.loop.create_connection(client_factory, *self.server_address)
                    self.connection = factory

                    self.auto_reconnect = True
                    self.im_message.connection_status = True
                    self.is_connected = True
                    self.do_reconnect = True
                    self.attempt_connect = False
                    print('here:3')
                    # print(factory)
                    print('here:4')
                    # asyncio.ensure_future(asyncio.Task(factory))
                    #self.connection = asyncio.Task(factory)
                    print(self.connection)
                    print(self.timeid)
                    client = self.loop.run_until_complete(factory)
                    print('here:5')
                    #client = self.loop.run_until_complete(task)
                    self.is_connected = False
                    #self.im_message.connection_status = False
                    # print(client)
                    print('here:6')
                    #self.is_connected = True
                    print('here:7')
                    # print(self.loop)
                except ConnectionRefusedError:
                    print('caught')
                except TimeoutError:
                    print('timeout')
                except OSError:
                    print("Server not up retrying in 5 seconds...")
                    self.is_connected = False
                    # yield from asyncio.sleep(5)
                else:
                    break

            await asyncio.sleep(1)

    async def read_loop(self):
        # print('read_loop')
        #counter = 0
        while True:
            #            if self.is_running:
            if self.state == self.ifConnected:
                # print('is_running')
                #print('in iface:read_loop')
                if self.im_message.connection_status:
                    #print('good status')
                    #start = time.time()
                    # srv.send_to_clients(sensor.read())
                    # if (False):
                    # print(self.im_message.has_output())
                    if (self.im_message.has_output()):
                        #counter += 1
                        # print(counter)
                        buffer = self.im_message.get_output()[0].decode('utf-8')
                        # buffer.strip('\r\n')
                        # print('strip')
                        # print(json.loads(buffer))
                        entry = {}
                        entry['DateTime'] = self.get_timestamp()
                        # print(entry)
                        # print(self.get_timestamp())
                        entry['InstrumentData'] = json.loads(buffer)
                        # print('entry')
                        # print(entry)
                        # self.read_buffer.append(entry)
                        # print(self.read_buffer)
                        # print(entry)
                        self.data.append(entry)
                        # print(self.data)
                    #end = time.time()
                    #delta = end-start
                    # while (delta > 1):
                    #    delta -= 1.0
                else:
                    self.is_connected = False
                #print('delta = %3.2f, sleep = %3.2f' % (delta, (1-delta)))
                # print("read_sensor")
                # await asyncio.sleep(1.0-delta)
            # print('sleep')
#            if counter > 10:
#                print(task)
#                self.connection.cancel()
#                print(task)
            await asyncio.sleep(0.1)

    async def check_connection(self):
        while True:
            #            print(self.im_message.connection_status)
            #            print(self.is_connected)
            #            print(self.auto_reconnect)
            #            print(self.connection)
            #            print(self.do_reconnect)

            if self.state == self.ifConnected:

                self.connection_timeout = 0
                if not self.im_message.connection_status:
                    self.state = self.ifDisconnected

            elif self.state == self.ifWaitingToConnect:
                self.connection_timeout += 1
                if self.im_message.connection_status:
                    self.state = self.ifConnected
                else:
                    if self.connection_timeout > 50:  # 5 seconds
                        self.state = self.ifDoConnect


#            if (not self.im_message.connection_status):
#                self.do_reconnect = True
#
#
#            if (not self.im_message.connection_status and
#                self.auto_reconnect):
#                #self.connection is not None):
#                print("connection is bad")
#                if (self.connection is not None):
#                    print('close_connection')
#                    self.connection.close()
#                    del self.connection
#                    self.connection = None
#                self.is_connected = False
#            else:
#                print('connected')
#                self.is_connected = True

            await asyncio.sleep(.1)

    def get_timestamp(self, timespec='seconds'):
        return datetime.utcnow().isoformat(timespec=timespec)

# class OLDTCPClient(asyncio.Protocol):
#
#    connections = {}
#
#    #def __init__(self, messages, future):
#    def __init__(self,signature):
#        super().__init__()
#        #self.messages = messages
#        self.log = logging.getLogger('TCPClient')
#        self.data_ready = False
#        self.buffer = ''
#        self.signature = signature
#        #self.f = future
#
#    def connection_made(self,transport):
#        self.transport = transport
#        self.address = transport.get_extra_info('peername')
#        self.log = logging.getLogger(
#            'TCPClient_{}_{}'.format(*self.address)
#        )
#        TCPClient.connections[self.signature] = {'data_ready':False, 'buffer':''}
#        #self.log.debug('connection accepted')
#        #SensorServer.clients[self.address] = self.transport
#        #print(SensorServer.clients)
#
#    def data_received(self,data):
#        #self.log.debug('received {!r}'.format(data))
#        self.buffer = data
#        #print(self.buffer.decode('utf-8'))
#        self.data_ready = True
#        TCPClient.connections[self.signature] = {'data_ready':True, 'buffer':data}
#        #print(TCPClient.connections)
#        #self.transport.write(data)
#        #self.log.debug('sent {!r}'.format(data))
#        #self.broadcast(data)
#
#    def eof_received(self):
#        self.log.debug('received EOF')
#        self.transport.close()
#        del TCPClient.connections[self.signaure]
#        #if self.transport.can_write_eof():
#        #    self.transport.write_eof()
#
#    def connection_lost(self,error):
#        self.log.debug('server closed connection')
#        self.transport.close()
#        del TCPClient.connections[self.signaure]
# if error:
##            self.log.error('ERROR: {}'.format(error))
# else:
# self.log.debug('closing')
##
##        del SensorServer.clients[self.address]
# print(SensorServer.clients)
#        super().connection_lost(error)
#
#    def has_data(signature):
#        return TCPClient.connections[signature]['data_ready']
#
#    def get_buffer(signature):
#        #print('buffer')
#        result = TCPClient.connections[signature]['buffer']
#        TCPClient.connections[signature] = {'data_ready':False, 'buffer':''}
#        #print(result)
#        return result
#
#


async def do_connection(iface, buffer):

    while True:
        print('do_connection: {}'.format(iface.do_reconnect))
        if iface.do_reconnect:
            if iface is not None:
                iface.stop()
                del iface
            try:
                iface = TCPInterface(SERVER_ADDRESS, buffer)
                iface.do_reconnect = False
                iface.start()

            except:
                iface = None

        await asyncio.sleep(5.0)


async def read_buffer(iface, data):
    while True:
        # write to clients
        # print("T=25.0,RH=34.5")
        # srv.send_to_clients("T=25.0,RH=34.5")
        #start = time.time()
        # srv.send_to_clients(sensor.read())
        # if (False):
        # print(iface.has_data())
        # print(iface.timeid)
        # if (iface['iface'] is not None and iface['iface'].has_data()):
        if (iface is not None and iface.has_data()):
            #buffer = iface['iface'].read()
            buffer = iface.read()
            #buffer = data.get()
            #print('buffer : ' + buffer)
            print('read_buffer:')
            print(buffer)
        #end = time.time()
        #delta = end-start
        # while (delta > 1):
        #    delta -= 1.0
        #print('delta = %3.2f, sleep = %3.2f' % (delta, (1-delta)))
        # print("read_sensor")
        # await asyncio.sleep(1.0-delta)
        await asyncio.sleep(1)
        # await asyncio.sleep(.5)
        # yield from asyncio.sleep(1)


def shutdown():
    # iface['iface'].stop()
    iface.stop()
    tasks = asyncio.Task.all_tasks()
    for t in tasks:
        # print(t)
        t.cancel()
    print("Tasks canceled")
    asyncio.get_event_loop().stop()
    # await asyncio.sleep(1)


#
if __name__ == "__main__":

    buffer = Data()

#    ifManager = InterfaceManager()
#    try:
#        iface = ifManager.createTCPInterface('TEST_INST',SERVER_ADDRESS,buffer)
#        iface['iface'].start()
#    except Exception as e:
#        print('main exception: {}'.format(e))

    event_loop = asyncio.get_event_loop()
    iface = TCPInterface(SERVER_ADDRESS, buffer)
    iface.start()
    # asyncio.ensure_future(do_connection(iface,buffer))

    #
#    signature = "abcdef"
#
#    #sensor = SHT31()
#    #sensor = HumiChip()
#    #sensor = DummyTRHP()
#    #tcp = TCPClient()
#    client_factory = functools.partial(
#        TCPClient,
#        signature=signature,
#    )
#
    #event_loop = asyncio.get_event_loop()
#    factory = event_loop.create_connection(client_factory, *SERVER_ADDRESS)
#    #factory = event_loop.create_connection(tcp, *SERVER_ADDRESS)
#    #server = asyncio.ensure_future(factory)
#    client = event_loop.run_until_complete(factory)
#
    task = asyncio.ensure_future(read_buffer(iface, buffer))
    task_list = asyncio.Task.all_tasks()
#
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
