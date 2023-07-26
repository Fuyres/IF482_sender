import os
import sys
import time
import queue
import threading
import datetime

import configparser

file_path = 'pynmea2/'
sys.path.append(os.path.dirname(file_path))
import pynmea2

file_path = 'serial/'
sys.path.append(os.path.dirname(file_path))
import serial

# import serial.tools.list_ports

queue = queue.Queue()


# ----------------------------------------------------------------------- #
# read GPS
# ----------------------------------------------------------------------- #
def serial_read(port, baud):
    # SerCon2 = serial.Serial(port, band, timeout=2.0)
    SerCon2 = serial.Serial()
    SerCon2.port = port
    SerCon2.baudrate = baud
    SerCon2.timeout = 2.0
    # ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
    # ser.parity = serial.PARITY_NONE  # set parity check: no parity
    # ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    # ser.timeout = None          #block read
    # ser.timeout = 0  # non blocking read
    # ser.xonxoff = False  # disable software flow control
    # ser.rtscts = False  # disable hardware (RTS/CTS) flow control
    # ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    # ser.writeTimeout = 2  # timeout for write

    try:
        SerCon2.open()
    except serial.SerialException as e:
        print('R Device error: {}'.format(e))
        exit()

    # ex_msg_valid = False

    while True:
        if SerCon2.isOpen():
            try:
                r_line = SerCon2.readline().decode('ascii', errors='replace')
                if "ZDA" in r_line:
                    msg = pynmea2.parse(r_line)
                    # print(repr(msg))

                    if msg.sentence_type == "ZDA":
                        # if "RMC"
                        queue.put(msg.datetime)
                        print("R pynmea2:", msg)
                        print("R GPS datetime:", msg.datetime)
                        print("R now:", datetime.datetime.now())
                        # break

                # if "RMC" in r_line:
                #    msg = pynmea2.parse(r_line)
                #    if msg.sentence_type == "RMC":
                #        print("R GPS is Valid:", msg.is_valid)
                #        ex_msg_valid = msg.is_valid

            except serial.SerialException as e:
                print('R Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('R Parse error: {}'.format(e))
                continue

    if SerCon2.isOpen():
        print('R Close serial port: {}'.format(SerCon2.port))
        SerCon2.close()


# ----------------------------------------------------------------------- #
# Write IF-482
# ----------------------------------------------------------------------- #
def serial_write(port, baud):
    # SerCon1 = serial.Serial(
    #    port=port,
    #    baudrate=band,
    #    timeout=2.0,
    #    bytesize=serial.SEVENBITS,
    #    parity=serial.PARITY_EVEN,
    #    stopbits=serial.STOPBITS_ONE)

    SerCon1 = serial.Serial()
    SerCon1.port = port
    SerCon1.baudrate = baud
    SerCon1.timeout = 2.0
    SerCon1.bytesize = serial.SEVENBITS
    SerCon1.parity = serial.PARITY_EVEN
    SerCon1.stopbits = serial.STOPBITS_ONE

    try:
        SerCon1.open()
    except serial.SerialException as e:
        print('W Device error: {}'.format(e))
        exit()

    # ex_msg_valid = False

    while True:
        if SerCon1.isOpen():
            if not queue.empty():
                now = queue.get()
                tgrm_f_str = "OAS" + now.strftime("%y%m%d%u%H%M%S") + "\r"
                str_1_encoded = tgrm_f_str.encode(encoding='ascii')

                print("W telegram: ", tgrm_f_str)
                print("W now:", datetime.datetime.now())
                print("\n")

                # for bytes in str_1_encoded:
                #    print("bytes: ", hex(bytes), end=' ')

                try:
                    SerCon1.write(str_1_encoded)
                    queue.task_done()
                    # break

                except serial.SerialException as e:
                    print('W Device error: {}'.format(e))
                    break
            else:
                time.sleep(0.1)

    if SerCon1.isOpen():
        print('W Close serial port: {}'.format(SerCon1.port))
        SerCon1.close()


# ----------------------------------------------------------------------- #
# config
# ----------------------------------------------------------------------- #
def save_config(path='config.cfg'):
    config = configparser.ConfigParser()

    config.add_section('IF842')
    config['IF842']['port'] = 'COM1'
    config['IF842']['baudrate'] = '9600'
    config['IF842']['timeout'] = '2.0'
    config['IF842']['bytesize'] = '7'
    config['IF842']['parity'] = 'E'
    config['IF842']['stopbits'] = '1'

    config.add_section('GPS')
    config['GPS']['port'] = 'COM2'
    config['GPS']['baudrate'] = '4800'
    config['GPS']['timeout'] = '2.0'
    # config['GPS']['bytesize'] = '8'
    # config['GPS']['parity'] = 'N'
    # config['GPS']['stopbits'] = '1'

    with open(path, 'w') as configfile:
        config.write(configfile)

    print("asra.cfg created")


def load_config(path='config.cfg'):
    config = configparser.ConfigParser()

    # if482
    port1 = 'COM1'
    baudrate1 = 9600
    timeout1 = 2.0
    bytesize1 = 7
    parity1 = 'E'
    stopbits1 = 1

    # gps
    port2 = 'COM2'
    baudrate2 = 4800
    timeout2 = 2.0
    bytesize2 = 8
    parity2 = 'N'
    stopbits2 = 1

    # read ini file
    if not config.read(path):
        print("Could not open ini-file: {0}".format(path))
        save_config()

    if config.has_section('Location'):
        if config.has_option('Location', 'Name'):
            name = config['Location']['Name']

        if config.has_option('Location', 'Region'):
            region = config['Location']['Region']

        if config.has_option('Location', 'Latitude'):
            latitude = float(config['Location']['Latitude'])

        if config.has_option('Location', 'Longitude'):
            longitude = float(config['Location']['Longitude'])

        if config.has_option('Location', 'Timezone'):
            timezone = config['Location']['Timezone']

    location_tmn = LocationInfo(name, region, timezone, latitude, longitude)
    log.debug("Load Config Astral:%s", location_tmn)

    if config.has_section('ModbusServer'):
        if config.has_option('ModbusServer', 'IP'):
            ip = config['ModbusServer']['IP']

        if config.has_option('ModbusServer', 'Port'):
            port = int(config['ModbusServer']['Port'])

    log.debug("Load Config Modbus:%s:%i", ip, port)

    return location_tmn, ip, port


# ----------------------------------------------------------------------- #
# Main
# ----------------------------------------------------------------------- #
if __name__ == '__main__':
    LocationTmn_, ip_, port_ = load_config()

    port1 = 'COM1'
    baud1 = 9600

    port2 = 'COM2'
    baud2 = 4800

    try:
        thread1 = threading.Thread(target=serial_read, args=(port2, baud2,), )
        thread1.daemon = True
        thread1.start()

        if True:  # need return from thread1
            thread2 = threading.Thread(target=serial_write, args=(port1, baud1,), )
            thread2.daemon = True
            thread2.start()
    except:
        print("M Error: unable to start thread")

    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        # thread 1 & 2 stop
        exit()
