"""
author: Xuanpeng Zhao
Date: Feb 07 2024
Description: This script is designed to decode UBX messages
"""
from pyublox.ublox_utility import UbloxUtils
from pyublox.ublox_constants import UbloxConst

class UBXDecoder:

    def __init__(self):
        self.meas = self.MEAS()
        self.alg = self.ALG()
    
    def decode(self, recv_data):
        header = recv_data[0] << 8 | recv_data[1] # recvData[0] & recvData[1] is the header
        msg_class = recv_data[2] # recvData[2] is the class
        msg_ID = recv_data[3] # recvData[3] is the ID
        if header == UbloxConst.HEADER_UBX:
            if msg_class == 16:
                if msg_ID == UbloxConst.ID_MEAS:
                    self.meas.decode(recv_data)

                if msg_ID == UbloxConst.ID_ALG:
                    #print("Received data:", recv_data)
                    self.alg.decode(recv_data)
        else:
            print("Wrong input for UBX decoder")

    class MEAS:
        def __init__(self):
            self.AccelX = None
            self.AccelY = None
            self.AccelZ = None
            self.GyroX = None
            self.GyroY = None
            self.GyroZ = None

        def decode(self, recv_data):
            # num_means is at recv_data[11] and only use the first 5 bits
            num_meas = (recv_data[11] & 0xF8) >> 3
            checksum = UbloxUtils.ubx_checksum(recv_data)
            if checksum == recv_data[-2:]:
                for i in range(num_meas):
                    # data is composed of 4 bytes and first 3 is data field and last one is data type
                    data = recv_data[6 + 8 + i * 4 : 6 + 8 + i * 4 + 4]
                    data_field = UbloxUtils.inverse_bytes_to_signed_decimal(data[0:3])
                    data_type = data[3] & 0x3F
                    
                    if data_type == 14:
                        self.GyroX = data_field / UbloxConst.DENOM
                    elif data_type == 13:
                        self.GyroY = data_field / UbloxConst.DENOM
                    elif data_type == 5:
                        self.GyroZ = data_field / UbloxConst.DENOM
                    elif data_type == 16:
                        self.AccelX = data_field / UbloxConst.DENOM
                    elif data_type == 17:
                        self.AccelY = data_field / UbloxConst.DENOM
                    elif data_type == 18:
                        self.AccelZ = data_field / UbloxConst.DENOM
                    elif data_type == 0:
                        print("UBX Decoder: ", "No data received")
            else:
                print("UBX Decoder: ", "Checksum error")
    class ALG:
        def __init__(self):
            self.yaw = None
            self.pitch = None
            self.roll = None
        def decode(self, recv_data):
            data = recv_data[6 + 8: 6 + 8 + 8]
            self.yaw =  int(UbloxUtils.inverse_bytes_to_hex(data[0:4]), 16) / UbloxConst.DENOM
            self.pitch =  int(UbloxUtils.inverse_bytes_to_hex(data[4:6]), 16) / UbloxConst.DENOM
            self.roll =  int(UbloxUtils.inverse_bytes_to_hex(data[6:8]), 16) / UbloxConst.DENOM    

    """
    To do: add more ubx data type, ID
    """

    
    
    