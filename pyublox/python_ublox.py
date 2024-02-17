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

class PythonUblox:
    def __init__(self, baud_rate=38400, device_port=None, enable_RTK=False, credential=None, mountpoint=None):
        if enable_RTK and credential is None:
            raise ValueError("Credentials must be provided when RTK is enabled.")
        self.__baud_rate = baud_rate
        self.__enable_RTK = enable_RTK
        self.__device_port = device_port # device_port Example: "COM3" on Windows or "/dev/ttyUSB0" on Linux
        self.__trying_enable_RTK_thread = None
        self.__credential = credential
        self.__mountpoint = mountpoint
        self.ntrip_connection = None
        self.ublox_connection = None
        self.nmea = NMEAReader()
        self.ubx = UBXDecoder()

         
        if self.__device_port is None:
            self.__device_port = UbloxUtils.find_ublox_device(UbloxConst.UBLOX_DEVICE)
        if self.__device_port is None:
            raise ValueError("No Device found.")
        
        self.ublox_connection = UBloxSerialConnection(self.__device_port, self.__baud_rate)
        self.ublox_connection.connect()

         
        
        # Enable RTK
        if self.__enable_RTK:
            self.__trying_enable_RTK_thread = threading.Thread(target=self.__create_ntrip_connection)
            self.__trying_enable_RTK_thread.start()
    
    def set_ublox_callback(self, callback):
        self.ublox_connection.set_callback(callback=callback)

    def __create_ntrip_connection(self):
        self.ntrip_connection = NTRIPSocketConnection(self.__credential["host"], self.__credential["port"], self.__credential["username"], self.__credential["password"], self.ublox_connection, mountpoint=self.__mountpoint)
        if self.__mountpoint is None:
            elapsed_time = 0
            while self.nmea.gga.lat is None and self.nmea.gga.lon is None:
                if elapsed_time >= 10: # 10 seconds timeout
                    print(f"NTRIP connection failed: Timeout waiting for GPS coordinates.")
                    return  # Exit the function if timeout is reached
                print(f"NTRIP connection waiting for valid GPS coordinates... {elapsed_time}s")
                time.sleep(1)  # Wait for a second before checking again
                elapsed_time += 1
            self.ntrip_connection.find_mountpoint(self.nmea.gga.lat, self.nmea.gga.lon)
        self.ntrip_connection.connect()

if __name__ == '__main__':
    # ublox_app = PythonUblox()
    ublox_app = PythonUblox(enable_RTK=True)
    