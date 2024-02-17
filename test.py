"""
author: Xuanpeng Zhao
Date: Feb 09 2024
Description: This script is the main user defined application
"""

from pyublox.python_ublox import PythonUblox
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst
from pyublox.ublox_serial_connection import UBloxSerialConnection


def main():

    credential = UbloxUtils.read_credentials(".\credentials.ini")
    def ublox_recv_data_callback(instance):
        global python_ublox
        if isinstance(instance, PythonUblox):
            python_ublox = instance
        if isinstance(instance, UBloxSerialConnection):
            data = instance.recv_data
            if data[0] == UbloxConst.HEADER_NMEA:
                python_ublox.nmea.decode(data)
            if (data[0] << 8 | data[1]) == UbloxConst.HEADER_UBX:
                python_ublox.ubx.decode(data)
                ### Write code here ###

                # if self.nmea.vtg.cog_mag:
                #     print(self.nmea.vtg.cog_mag) # heading
                 
                ### --------------- ###
    python_ublox = PythonUblox(credential=credential, ublox_recv_data_callback=ublox_recv_data_callback)

if __name__ == '__main__':
    main()
    