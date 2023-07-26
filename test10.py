from sys import platform
import os
import sys
import time
import threading
import datetime

file_path = 'pynmea2/'
sys.path.append(os.path.dirname(file_path))
import pynmea2

file_path = 'serial/'
sys.path.append(os.path.dirname(file_path))
import serial

# import serial.tools.list_ports


# lock to serialize console output
lock = threading.Lock()
ex_msg = None
#event = threading.Event()


def serial_read(port, band, lock):
    global ex_msg
    SerCon2 = serial.Serial(port, band, timeout=2.0)

    while True:
        try:
            r_line = SerCon2.readline().decode('ascii', errors='replace')
            if "ZDA" in r_line:
                msg = pynmea2.parse(r_line)

                if msg.sentence_type == "ZDA":
                    with lock:
                        print("msg:", msg)
                        print("msg datetime:", msg.datetime)
                        print("now:", datetime.datetime.now())
                        print("\n")
                        ex_msg = msg.datetime
                        # break

        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue


def serial_write(port, band, lock):
    SerCon1 = serial.Serial(
        port=port,
        baudrate=band,
        timeout=2.0,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE)

    while True:
        global ex_msg
        now = None

        with lock:
            if ex_msg is not None:
                now = ex_msg
                ex_msg = None

        if now is not None:
            tgrm_f_str = "OAS" + now.strftime("%y%m%d%u%H%M%S") + "\r"
            str_1_encoded = tgrm_f_str.encode(encoding='ascii')

            print("telegram: ", tgrm_f_str)
            print("now:", datetime.datetime.now())
            print("\n")

            try:
                SerCon1.write(str_1_encoded)
                # break

            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                break
        else:
            time.sleep(0.1)


if __name__ == '__main__':

    port1 = 'COM1'
    band1 = 9600

    port2 = 'COM2'
    band2 = 4800

    # Create two threads as follows
    try:
        thread1 = threading.Thread(target=serial_read, args=(port2, band2, lock, ), )
        thread1.daemon = True
        thread1.start()

        if True:  # need return from thread1
            thread2 = threading.Thread(target=serial_write, args=(port1, band1, lock, ), )
            thread2.daemon = True
            thread2.start()
    except:
        print("Error: unable to start thread")

    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        exit()
