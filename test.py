"""
author: Xuanpeng Zhao
Date: Feb 09 2024
Description: This script is the main user defined application
"""

from pyublox.python_ublox import PythonUblox
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst


class main:

    def __init__(self):
        

        # credential = UbloxUtils.read_credentials(".\credentials.ini")
        self.python_ublox = PythonUblox()
        self.python_ublox.set_ublox_callback(callback=self.ublox_recv_data_callback)

    def ublox_recv_data_callback(self, data):
        if len(data) > 1:
            if data[0:2] == UbloxConst.HEADER_NMEA:
                self.python_ublox.nmea.decode(data)
                # print(self.python_ublox.nmea.gga.quality)
                print(self.python_ublox.nmea.vtg.cog_mag) # heading
                print(self.python_ublox.nmea.gga.lat) # lat
                print(self.python_ublox.nmea.gga.lon) # lon 
                print(self.python_ublox.nmea.gga.alt) # lon   

            elif data[0:2] == UbloxConst.HEADER_UBX:
                pass
                #self.python_ublox.ubx.decode(data)
                #print(f"""yaw {self.python_ublox.ubx.alg.yaw} pitch {self.python_ublox.ubx.alg.pitch} roll {self.python_ublox.ubx.alg.roll}""")
            else:
                # print("Unknown data: ", data)
                pass



if __name__ == '__main__':
    main()
    