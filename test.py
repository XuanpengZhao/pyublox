"""
author: Xuanpeng Zhao
Date: Feb 09 2024
Description: This script is the main user defined application
"""

from pyublox.python_ublox import PythonUblox
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst
from pyublox.ublox_serial_connection import UBloxSerialConnection


class main:

    def __init__(self):
        

        credential = UbloxUtils.read_credentials(".\credentials.ini")
        self.python_ublox = PythonUblox(credential=credential)
        self.python_ublox.set_ublox_callback(callback=self.ublox_recv_data_callback)

    def ublox_recv_data_callback(self, data):
        if data[0] == UbloxConst.HEADER_NMEA:
            self.python_ublox.nmea.decode(data)
        if (data[0] << 8 | data[1]) == UbloxConst.HEADER_UBX:
            self.python_ublox.ubx.decode(data)
            ### Write code here ###

            # if self.nmea.vtg.cog_mag:
            #     print(self.nmea.vtg.cog_mag) # heading
                
            ### --------------- ###


if __name__ == '__main__':
    main()
    