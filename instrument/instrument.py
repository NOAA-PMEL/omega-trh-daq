#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:52:35 2018

@author: derek
"""

import asyncio
from tcpinterface import TCPInterface
from data import Data
from datafile import DataFile
import time
import math
from datetime import datetime


class EnvSensor():

    def __init__(self, config):

        self.data = Data()

        self.config = config

        self.instrument_class = 'env_sensor'
        self.name = config['instrument_name']

        server_address = (config['interface_config']['host'],
                          config['interface_config']['port'])
        self.iface = TCPInterface(server_address, self.data)
        self.iface.start()

        df_config = {
            'base_path': config['datafile_config']['base_path'],
            'instrument_class': self.instrument_class,
            'instrument_name': self.name,
            'write_freq': config['datafile_config']['write_freq'],
        }

        self.data_file = DataFile(df_config)

        self.out_dt = ''
        self.out_data = {}
        #self.data = None
        self.task_list = []

    def start(self):
        print("Starting EnvSensor")
        #self.attempt_connect = True
        task = asyncio.ensure_future(self.read_loop())
        self.task_list.append(task)
        self.is_running = True

    def stop(self):
        self.iface.stop()
        #tasks = asyncio.Task.all_tasks()
        for t in self.task_list:
            # print('stop:')
            # print(t)
            t.cancel()
            self.task_list.remove(t)
            # tasks.remove(t)
        self.is_running = False
        self.attempt_connect = False

    async def read_loop(self):

        last_read = datetime.now()
        # print(last_read)
        while True:
            # print(self.iface.has_data())
            if (self.iface.has_data()):
                # print('here')
                buffer = self.iface.read()[0]
                # print(buffer)
                # print('here2')
                dt = buffer['DateTime']
                # print(dt)
                #buf = buffer['Data']
                # print(buf)
                # print(buffer['Data']['RH']['value'])
                # print(buffer['Data']['RH'])
                buf = buffer['InstrumentData']
                # print(buf)
                meas_list = buf['METADATA']['MeasurementList']
                # print(meas_list)
                self.out_dt = dt
                #dat = {}
                out = ''
                for meas in meas_list:
                    value = buf['DATA'][meas]['value']
                    units = buf['DATA'][meas]['units']
                    self.out_data[meas] = {
                        'value': buf['DATA'][meas]['value'],
                        'units': buf['DATA'][meas]['units'],
                    }
                    # print(meas)
                    # print(dat)
                    # print(self.out_data)
                    # print(type(value))
                    # print(units)
                    out += '  {}={:.2f}{}'.format(meas, value, units)
                    # print(out)
                #t = buffer['Data']['Temperature']['value']
                #rh = buffer['Data']['RH']['value']
                # print(rh)
                #print('[{}] -- {} : T={}C, RH={}%'.format(self.name,dt,t,rh))
                #print('[{}] -- {} : {}'.format(self.name,dt,out))

                self.data_file.append(buffer)
                last_read = datetime.now()
                # print(last_read)

                #buffer = data.get()
                #print('buffer : ' + buffer)
                # print('read_buffer:')
                # print(buffer)
            delta = (datetime.now()-last_read).total_seconds()
            # print(delta)
            if delta > 5.0:
                self.out_dt = ''
                self.out_data = {}
#                pass

            await asyncio.sleep(0.1)


def time_to_next(sec):
    now = time.time()
    delta = sec - (math.fmod(now, sec))
    return delta


async def output_to_screen(sensor_list):

    # wait until exact second

    while True:

        start = time.time()

        for sensor in sensor_list:
            data = sensor.out_data
            out = ''
            for key in data:
                value = data[key]['value']
                units = data[key]['units']
                # print(type(value))
                # print(units)
                out += '  {}={:.2f}{}'.format(key, value, units)
                # print(out)
            #t = buffer['Data']['Temperature']['value']
            #rh = buffer['Data']['RH']['value']
            # print(rh)
            #print('[{}] -- {} : T={}C, RH={}%'.format(self.name,dt,t,rh))
            print('[{}] -- {} : {}'.format(sensor.name, sensor.out_dt, out))
        print('------')
        end = time.time()
        delta = end-start
        while (delta > 1):
            delta -= 1.0

#        print('beat')
#        print('-------------------------------')
        #print(chr(27) + "[2J")
        # pass

        await asyncio.sleep(time_to_next(1))
        # await asyncio.sleep(1.0-delta)


def shutdown(sensor_list):
    print('shutdown:')
    for sensor in sensor_list:
        # print(sensor)
        sensor.stop()

    tasks = asyncio.Task.all_tasks()
    for t in tasks:
        # print(t)
        t.cancel()
    print("Tasks canceled")
    asyncio.get_event_loop().stop()
    # await asyncio.sleep(1)


#
if __name__ == "__main__":

    TEST = False
    sensor_list = []

# DEFINE Sensors
    if not TEST:

        config_df_base = {
            'base_path': '/home/junge/acg/Data',
            'write_freq': 10,
        }

        # CCNSMPS_sheath
        config_ccnsmps_sheath_iface = {
            'host': '10.55.169.113',
            'port': 8199,
        }
        config_ccnsmps_sheath = {
            'instrument_name': 'CCN_SMPS_Sheath',
            'interface_config': config_ccnsmps_sheath_iface,
            'datafile_config': config_df_base
        }
        sensor = EnvSensor(config_ccnsmps_sheath)
        sensor.start()
        sensor_list.append(sensor)

        # CCN_cpc_inlet
        config_ccncpc_in_iface = {
            'host': '10.55.169.117',
            'port': 8199,
        }
        config_ccncpc_inlet = {
            'instrument_name': 'CCN_CPC_Inlet',
            'interface_config': config_ccncpc_in_iface,
            'datafile_config': config_df_base
        }
        sensor = EnvSensor(config_ccncpc_inlet)
        sensor.start()
        sensor_list.append(sensor)

        # MART_SMPS_sheath
        config_mart_smps_sheath_iface = {
            'host': '10.55.169.119',
            'port': 8199,
        }
        config_mart_smps_sheath = {
            'instrument_name': 'MART_SMPS_Sheath',
            'interface_config': config_mart_smps_sheath_iface,
            'datafile_config': config_df_base
        }
        sensor = EnvSensor(config_mart_smps_sheath)
        sensor.start()
        sensor_list.append(sensor)

        # ThSMPS_cpc_inlet
        config_thcpc_in_iface = {
            'host': '10.55.169.115',
            'port': 8199,
        }
        config_thcpc_inlet = {
            'instrument_name': 'ThSMPS_CPC_Inlet',
            'interface_config': config_thcpc_in_iface,
            'datafile_config': config_df_base
        }
        sensor = EnvSensor(config_thcpc_inlet)
        sensor.start()
        sensor_list.append(sensor)

        # Nafion4_outlet
        config_nafion4_out_iface = {
            'host': '10.55.169.112',
            'port': 8199,
        }
        config_nafion4_outlet = {
            'instrument_name': 'Nafion4_outlet',
            'interface_config': config_nafion4_out_iface,
            'datafile_config': config_df_base
        }
        sensor = EnvSensor(config_nafion4_outlet)
        sensor.start()
        sensor_list.append(sensor)

# End define
    else:

        # TestSensor

        config_df_test = {
            'base_path': '/home/horton/acg/tmp/Data',
            'write_freq': 10,
        }
        config_test_iface = {
            'host': 'localhost',
            'port': 8199,
        }
        config_test = {
            'instrument_name': 'DummySensor',
            'interface_config': config_test_iface,
            'datafile_config': config_df_test,
        }
        sensor = EnvSensor(config_test)
        sensor.start()
        sensor_list.append(sensor)

    event_loop = asyncio.get_event_loop()

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
#    task = asyncio.ensure_future(heartbeat())
    task = asyncio.ensure_future(output_to_screen(sensor_list))
    task_list = asyncio.Task.all_tasks()
#
    try:
        event_loop.run_until_complete(asyncio.wait(task_list))
        # event_loop.run_forever()
    except KeyboardInterrupt:
        print('closing client')
        # client.close()
        # event_loop.run_until_complete(client.wait_closed())

        shutdown(sensor_list)
#        for task in task_list:
#            print("cancel task")
#            task.cancel()
        # server.close()
        event_loop.run_forever()
        # event_loop.run_until_complete(asyncio.wait(asyncio.ensure_future(shutdown)))

    finally:

        print('closing event loop')
        event_loop.close()
