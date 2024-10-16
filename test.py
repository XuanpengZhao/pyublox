"""
author: Xuanpeng Zhao
Date: Feb 09 2024
Description: This script is the main user defined application
"""

from pyublox.python_ublox import PythonUblox
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst
from datetime import datetime
import csv
import time

class main:

    def __init__(self):
        
        # credential = UbloxUtils.read_credentials(".\credentials.ini", tag="UCR")
        self.python_ublox = PythonUblox()
        self.python_ublox.connect()
        self.python_ublox.set_ublox_callback(callback=self.ublox_recv_data_callback)
        # self.python_ublox.enable_RTK(credential, mountpoint="U-BLOX")

        timeSaved = time.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = f"Ublox_GPS_{timeSaved}.csv"
        self.csv_file = open('logs/' + fileName, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Altitude', 'GNSS_Time', 'Quality', 'NumSatellites', "Local_Datatime"])


    def ublox_recv_data_callback(self, data):
        if len(data) > 1:
            if data[0:2] == UbloxConst.HEADER_NMEA:
                self.python_ublox.nmea.decode(data)
                # print(self.python_ublox.nmea.vtg.cog_mag) # heading
                current_datetime = datetime.now()
                print(current_datetime)
                print(self.python_ublox.nmea.gga.lat) # lat
                print(self.python_ublox.nmea.gga.lon) # lon 
                print(self.python_ublox.nmea.gga.alt) # lon   
                print(self.python_ublox.nmea.gga.time) # time  
                print(self.python_ublox.nmea.gga.quality)
                print(self.python_ublox.nmea.gga.numSV)
                lat = self.python_ublox.nmea.gga.lat
                lon = self.python_ublox.nmea.gga.lon
                alt = self.python_ublox.nmea.gga.alt
                time = self.python_ublox.nmea.gga.time
                quality = self.python_ublox.nmea.gga.quality
                numSV = self.python_ublox.nmea.gga.numSV
                self.csv_writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), lat, lon, alt, time, quality, numSV, current_datetime])

            elif data[0:2] == UbloxConst.HEADER_UBX:
                pass
                #self.python_ublox.ubx.decode(data)
                #print(f"""yaw {self.python_ublox.ubx.alg.yaw} pitch {self.python_ublox.ubx.alg.pitch} roll {self.python_ublox.ubx.alg.roll}""")
            else:
                # print("Unknown data: ", data)
                pass



if __name__ == '__main__':
    main()
    