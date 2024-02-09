"""
author: Xuanpeng Zhao
Date: Feb 09 2024
Description: This script is the main user defined application
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
    def __init__(self, baud_rate=38400, device_port="COM10", enable_RTK=False):
        self.__baud_rate = baud_rate
        self.__enable_RTK = enable_RTK
        self.__device_port = None # device_port Example: "COM3" on Windows or "/dev/ttyUSB0" on Linux
        self.__trying_enable_RTK_thread = None
        self.ntrip_connection = None
        self.ublox_connection = None
        
        self.nmea_reader = NMEAReader()
        self.ubx_decoder = UBXDecoder()
        self.__device_port = UbloxUtils.find_ublox_device(UbloxConst.UBLOX_DEVICE)
        if self.__device_port is None:
            print("Device not found")
        else:
            # Default device_port
            self.__device_port = device_port
        
        self.ublox_connection = UBloxSerialConnection(self.__device_port, self.__baud_rate, self.ublox_recv_data_callback)
        self.ublox_connection.connect()
        
        # Enable RTK
        if self.__enable_RTK:
            self.__trying_enable_RTK_thread = threading.Thread(target=self.create_ntrip_connection)
            self.__trying_enable_RTK_thread.start()

    def create_ntrip_connection(self):
        credential = UbloxUtils.read_credentials(".\credentials.ini")
        self.ntrip_connection = NTRIPSocketConnection(credential["host"], credential["port"], credential["username"], credential["password"], self.ublox_connection)
        elapsed_time = 0
        self.nmea_reader.gga.lat = 33.974584
        self.nmea_reader.gga.lon = -117.316830
        while not self.nmea_reader.gga.lat or not self.nmea_reader.gga.lon:
            if elapsed_time >= 10: # 10 seconds timeout
                print(f"NTRIP connection failed: Timeout waiting for GPS coordinates.")
                return  # Exit the function if timeout is reached
            print(f"NTRIP connection waiting for valid GPS coordinates... {elapsed_time}s")
            time.sleep(1)  # Wait for a second before checking again
            elapsed_time += 1
   
        self.ntrip_connection.find_closest_ntrip_source(self.nmea_reader.gga.lat, self.nmea_reader.gga.lon)
        self.ntrip_connection.connect()

    def ublox_recv_data_callback(self, data):
        if data:
            if data[0] == UbloxConst.HEADER_NMEA:
                self.nmea_reader.decode(data)
            if (data[0] << 8 | data[1]) == UbloxConst.HEADER_UBX:
                self.ubx_decoder.decode(data)
                ### Write code here ###

                # if self.nmea_reader.vtg.cog_mag:
                #     print(self.nmea_reader.vtg.cog_mag) # heading
                 
                ### --------------- ###
                 

if __name__ == '__main__':
    # ublox_app = PythonUblox()
    ublox_app = PythonUblox(enable_RTK=True)
    