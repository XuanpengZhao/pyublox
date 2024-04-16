"""
author: Xuanpeng Zhao
Date: Feb 16 2024
Description: This script is the main pyublox initializer
"""
import time
from pyublox.ublox_serial_connection import UBloxSerialConnection
from pyublox.ubx_decoder import UBXDecoder
from pyublox.nmea_reader import NMEAReader
from pyublox.ublox_constants import UbloxConst
from pyublox.ublox_utility import UbloxUtils
from pyublox.ntrip_socket_connection import NTRIPSocketConnection
import threading
import configparser

class PythonUblox:
    def __init__(self):
        self.__enable_RTK_thread = None
        self.__ntrip_connection = None
        self.__ublox_connection = None
        self.nmea = NMEAReader()
        self.ubx = UBXDecoder()

    def connect(self, baud_rate=38400, device_port=None):
        self.__baud_rate = baud_rate
        self.__device_port = device_port # device_port Example: "COM3" on Windows or "/dev/ttyUSB0" on Linux
        if self.__device_port is None:
            self.__device_port = UbloxUtils.find_ublox_device(UbloxConst.UBLOX_DEVICE)
        if self.__device_port is None:
            raise ValueError("No Device found.")
        self.__ublox_connection = UBloxSerialConnection(self.__device_port, self.__baud_rate)
        self.__ublox_connection.connect()

        # Enable RTK
    def enable_RTK(self, credential, mountpoint=None):
        self.__mountpoint = mountpoint
        if credential:
            self.__enable_RTK_thread = threading.Thread(target=self.__create_ntrip_connection, args=(credential,))
            self.__enable_RTK_thread.start()
        else:
            raise ValueError("Credentials must be provided when RTK is enabled.")
    
    def set_ublox_callback(self, callback):
        if self.__ublox_connection:
            self.__ublox_connection.set_callback(callback=callback)
        else:
            raise ValueError("Must connect ublox before set callback.")

    def __create_ntrip_connection(self, credential):
        self.__ntrip_connection = NTRIPSocketConnection(credential["host"], credential["port"], credential["username"], credential["password"], self.__ublox_connection, mountpoint=self.__mountpoint)
        if self.__mountpoint is None:
            elapsed_time = 0
            while self.nmea.gga.lat is None and self.nmea.gga.lon is None:
                if elapsed_time >= 10: # 10 seconds timeout
                    print(f"NTRIP connection failed: Timeout waiting for GPS coordinates.")
                    return  # Exit the function if timeout is reached
                print(f"NTRIP connection waiting for valid GPS coordinates... {elapsed_time}s")
                time.sleep(1)  # Wait for a second before checking again
                elapsed_time += 1
            self.__ntrip_connection.find_mountpoint(self.nmea.gga.lat, self.nmea.gga.lon)
        self.__ntrip_connection.connect()

if __name__ == '__main__':
    # ublox_app = PythonUblox()
    ublox_app = PythonUblox()
    