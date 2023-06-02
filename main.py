from sys import platform
import argparse
import os
import sys
import time
from datetime import datetime

file_path = 'serial/'
sys.path.append(os.path.dirname(file_path))
import serial
import serial.tools.list_ports


# no need now
class SerialRun(object):
    def __init__(self, serialport="COM1"):
        self.SerialPort = serialport
        self.ReadBaudrate = 9600
        self.WriteBaundrate = 9600
        self.SerCon = None

    def connect(self):
        self.SerCon = serial.Serial(
            port=self.SerialPort,
            baudrate=9600,
            timeout=5.0,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE)

        print("Connected to Serial Port: " + self.SerCon.portstr)
        return self.SerCon.is_open

    def disconnect(self):
        if self.SerCon.is_open:
            self.SerCon.close()

    def run(self):
        if self.connect():
            # bytes_command = command_list.cmd_dict[self.cmd_id].cmd.encode()
            # CommandsDEC[self.cmd_id].encode()
            # self.send_command(bytes_command)

            # print("get string")
            # buffer_str = self.read_bytes(command_list.cmd_dict[self.cmd_id].LenData)
            # self.read_bytes(LenData[self.cmd_id])

            return ""  # buffer_str

    def get_strings(self):
        str = self.run()
        print(str)

    def get_str(self):
        str0 = self.run()
        str1 = ""
        if len(str0) > 0:
            str1, str_tag = str0
        return str1

    def read_bytes(self, lines=1):
        self.SerCon.baudrate = self.ReadBaudrate
        # print("Set Read baudrate: ", self.SerCon.baudrate)

        # buffer_str += "\n"
        # print("buffer_str:", buffer_str)

        # read LINES
        j = 0
        reading_ba = bytearray()
        reading_ba_line = bytearray()
        # reading_ba_out = bytearray()

        while j < lines:
            for buffer in self.SerCon.read():
                reading_ba.append(buffer)
                reading_ba_line.append(buffer)
                if buffer == 0x0D:  # dot
                    j += 1
                    # reading_ba_out += reading_ba
                    print("xl:", j, reading_ba_line)
                    reading_ba_line = bytearray()

            # print("reading:", reading_ba)
            # print("reading2:", reading_ba_out.de)

        self.disconnect()

        # buffer_str += reading_ba_out.decode()
        # str1 = reading_ba_out.decode()
        buffer_str = ""
        buffer_str += reading_ba.decode()

        # str1 = str1.replace('\r', '\n')
        buffer_str = buffer_str.replace('\r', '\n')
        buffer_str = buffer_str[:3] + '\n' + buffer_str[3:]

        # print("buffer_str: \n", buffer_str)
        return buffer_str

    def send_command(self, comd):
        self.SerCon.baudrate = self.WriteBaundrate
        # print("Set Write baudrate: ", self.SerCon.baudrate)
        self.SerCon.write(comd)
        time.sleep(1)


def portIsUsable(portName):
    try:
        ser = serial.Serial(port=portName)
        return True
    except:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="IF-482 Sender")
    parser.add_argument("-d", "--device", type=str, help="Serial port for IF-482. Example: "
                                                         "/dev/ttyS1 or COM1 or test", required=True)
    # parser.add_argument("--verbose", help="Make this script more verbose", action="store_true")

    args = parser.parse_args()

    if args.device != 'test':

        SerialPortsTuple = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        print(SerialPortsTuple)

        # check if serial port exist
        SerialFound = ""
        for i in range(0, len(SerialPortsTuple)):
            if SerialPortsTuple[i][0] == args.device:
                print("Device was found successful: %s" % SerialPortsTuple[i][1])
                SerialFound = SerialPortsTuple[i][0]

        if len(SerialFound) < 1:
            print("Error! failed to locate specified device: %s" % args.device)
            sys.exit(1)

        # check if serial port busy
        if portIsUsable(args.device):
            print("Port is not busy.")
        else:
            print("Port is Busy!")
            sys.exit(1)

    SerCon = serial.Serial(
        port=args.device,
        baudrate=9600,
        timeout=5.0,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE)

    if not SerCon.is_open:
        SerCon.open()

    while True:
        now = datetime.now()
        # tgrm_f_str = "OAS" + now.strftime("%y%m%d%u%H%M%S") + "\r"
        # tgrm_f_str = "OAL " + now.strftime("%y %m %d %u %H %M %S") + "\r"
        # print("telegram", tgrm_f_str)
        tgrm_f_str = "OAS" + now.strftime("%y%m%d%u%H%M%S") + "\r"
        str_1_encoded = tgrm_f_str.encode(encoding='ascii')


        print("telegram: ", tgrm_f_str)

        # printing individual bytes
        for bytes in str_1_encoded:
            print("bytes: ", hex(bytes), end=' ')

        SerCon.write(str_1_encoded)
        # time.sleep(1)
        # while True:
        #try:
        #    print("Attempt to Read")
        #    readOut = SerCon.readline().decode('ascii')
            # time.sleep(1)
        #    print("Reading: ", readOut)
        #    break
        #except:
        #    pass
        #print("Restart")
        #SerCon.flush()

        # x = ser.read()  # read one byte
        # s = ser.read(10)  # read up to ten bytes (timeout)

        time.sleep(5*60)

    if SerCon.is_open:
        SerCon.close()

###############################
# for c in test:
#    print(hex(ord(c)))

# To convert:
# output = ''.join(hex(ord(c)) for c in test)

# or without the '0x' in output:
# output = ''.join(hex(ord(c))[2:] for c in test)
